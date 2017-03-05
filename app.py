from flask import Flask, render_template, redirect, request, url_for, session, send_from_directory
from flask_cors import CORS
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from system.io import FileHandler
from system import crawler
from system.structure import ProcessQueue
import os
import time
import thread
import config
from bs4 import BeautifulSoup

# Process queue
process_queue = None

# Firefox selenium driver
driver = None

# Initialising state
initialised = False

app = Flask(__name__)
CORS(app)


def initSystem():
    global process_queue, driver

    # Initialising variables
    # Setting up process queue
    file_handler = FileHandler(config.prop['LINK_LIST_PATH'])
    process_queue = ProcessQueue(file_handler.read())

    # Selenium Firefox driver
    driver = webdriver.Firefox(executable_path=os.getcwd() + '/driver/geckodriver')

    # Setting up sessions
    file_handler = FileHandler(config.prop['COMPANY_LIST_PATH'])
    session['company_list'] = file_handler.read()

    file_handler = FileHandler(config.prop['LINK_LIST_PATH'])
    session['link_list'] = file_handler.read()

    # Load configuration
    config.loadConfig()


def process():
    global driver, process_queue

    while config.prop['PROCEED']:
        url = process_queue.dequeue()
        if url is None:
            break

        while True:
            driver.get(url)
            try:
                input_element = driver.find_element_by_id("captcha_data.solution")
                input_element.send_keys('')
            except NoSuchElementException:
                pass

            try:
                element = driver.find_element_by_id("begin_pub")
                soup = BeautifulSoup(driver.page_source, "lxml")
                print soup.prettify()
                break
            except NoSuchElementException:
                time.sleep(config.prop['SLEEP_TIME'])


@app.route('/')
def index():
    global initialised, driver
    if not initialised:
        initSystem()
        initialised = True
    return render_template('main.html')


@app.route('/start_process')
def startProcess():
    print "Server :", "Running"
    session['system_state'] = 'Running'
    config.prop['PROCEED'] = True
    thread.start_new_thread(process, ())
    # process()
    return redirect('/')


@app.route('/stop_process')
def stopProcess():
    print "Server :", "Idle"
    session['system_state'] = 'Idle'
    global process_queue
    if not isinstance(process_queue, ProcessQueue):
        session['error'] = 'stopProcess > not a ProcessQueue'
        return redirect('/')

    file_handler = FileHandler(config.prop['LINK_LIST_PATH'])
    file_handler.write(process_queue.getItems())
    config.prop['PROCEED'] = False
    return redirect('/')


@app.route('/load_url_list')
def loadURLList():
    global process_queue

    if not isinstance(process_queue, ProcessQueue):
        session['error'] = 'loadURLList > not a ProcessQueue'
        return redirect('/')

    file_handler = FileHandler(file_name=config.prop['COMPANY_LIST_PATH'])
    company_list = file_handler.read()

    links = []
    for company in company_list:
        links.extend(crawler.getSearchUrls(company))

    file_handler = FileHandler(file_name=config.prop['LINK_LIST_PATH'])
    file_handler.write(links)

    initSystem()

    return redirect('/')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True, port=4000)


