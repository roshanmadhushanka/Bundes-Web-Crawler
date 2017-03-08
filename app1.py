import os
import thread
import time
import config

from bs4 import BeautifulSoup
from flask import Flask, render_template, redirect, session
from flask_cors import CORS
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from system import crawler
from system.io import FileHandler
from system.structure import ProcessQueue
from system.process import Async

# Process queue
process_queue = None

# Firefox selenium driver
driver = None

# Initialising state
initialised = False

prcd = False

app = Flask(__name__)
CORS(app)

# Asynchronous queue
async = None


def initSystem():
    global process_queue, driver, async

    # Initialising variables
    # Setting up process queue
    file_handler = FileHandler(config.prop['LINK_LIST_PATH'])
    process_queue = ProcessQueue(file_handler.read())

    # Selenium Firefox driver
    driver = webdriver.Firefox(executable_path=os.getcwd() + '/driver/geckodriver')

    # Aasynchrnous process handler
    async = Async(driver=driver, process_q=process_queue)
    async.start()

    # Setting up sessions
    file_handler = FileHandler(config.prop['COMPANY_LIST_PATH'])
    session['company_list'] = file_handler.read()

    file_handler = FileHandler(config.prop['LINK_LIST_PATH'])
    session['link_list'] = file_handler.read()

    # Load configuration
    config.loadConfig()


def saveSystemState():
    '''
    Save system state
    :return:
    '''
    global process_queue
    if not isinstance(process_queue, ProcessQueue):
        return

    config.saveConfig()
    file_handler = FileHandler(config.prop['LINK_LIST_PATH'])
    file_handler.write(process_queue.getItems())


@app.route('/')
def index():
    global initialised, driver
    if not initialised:
        initSystem()
        initialised = True
    return render_template('main.html')


@app.route('/start_process')
def startProcess():
    global async
    print "Server :", "Running"
    session['system_state'] = 'Running'

    async.resume()

    return redirect('/')


@app.route('/stop_process')
def stopProcess():
    global async

    print "Server :", "Idle"
    session['system_state'] = 'Idle'

    async.pause()

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


