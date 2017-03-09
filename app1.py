import os
import socket

import config

from flask import Flask, render_template, redirect, session
from flask_cors import CORS
from selenium import webdriver
from system import crawler
from system.io import FileHandler
from system.process import Async
from system.structure import ProcessQueue

# Process queue
process_queue = None

# Firefox selenium driver
driver = None

# Initialising state
initialised = False

app = Flask(__name__)
CORS(app)

# Asynchronous queue
async = None


def isInternetAvailable(host="8.8.8.8", port=53, timeout=3):
    '''
    Check for internet connection availability
    :param host: google-public-dns-a.google.com
    :param port: 53/tcp
    :param timeout: 3 second waiting time to get a response from google server
    :return:
    '''
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception as ex:
        return False


def initSystem():
    global process_queue, driver, async

    # Initialising variables
    # Retrieve
    file_handler = FileHandler(file_name=config.prop['COMPANY_LIST_PATH'])
    company_list = file_handler.read()

    # Check for internet connection before crawling
    if not isInternetAvailable():
        session['error'] = "Check for internet connection"
        print "Check for internet connection"
        return

    # Load links to the system via internet
    links = []
    for company in company_list:
        links.extend(crawler.getSearchUrls(company))

    file_handler = FileHandler(file_name=config.prop['LINK_LIST_PATH'])
    file_handler.write(links)

    # Setting up process queue
    process_queue = ProcessQueue(links)

    # Selenium Firefox driver
    driver = webdriver.Firefox(executable_path=os.getcwd() + '/driver/geckodriver')

    # Asynchronous process handler
    async = Async(driver=driver, process_q=process_queue)
    async.start()

    # Setting up session
    session['link_list'] = links
    session['company_list'] = company_list

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


