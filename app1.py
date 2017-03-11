import os
from urllib2 import URLError

import config
from flask import Flask, render_template, redirect, session, request
from flask_cors import CORS
from selenium import webdriver
from system import crawler
from system.io import FileHandler
from system.process import Async
from system.structure import ProcessQueue, NextQueue

# Company list
company_queue = None

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


def initSystem():
    global process_queue, driver, async, company_queue

    # Initialising variables
    # Retrieve
    file_handler = FileHandler(file_name=config.COMPANY_LIST_PATH)
    company_list = file_handler.read()

    if company_list is None:
        session['error'] = 'Company list cannot be found'
        return

    # Load links to the system via internet
    company_queue = NextQueue(company_list)

    links = []
    for company in company_list:
        try:
            links.extend(crawler.getSearchUrls(company))
        except URLError:
            session['error'] = 'Connection timeout'
            return

    file_handler = FileHandler(file_name=config.LINK_LIST_PATH)
    file_handler.write(links)

    # Setting up process queue
    process_queue = ProcessQueue(links)

    # Selenium Firefox driver
    print config.GECKODRIVER_PATH
    driver = webdriver.Firefox(executable_path=config.GECKODRIVER_PATH)
    driver.start_client()

    # Asynchronous process handler
    async = Async(driver=driver, process_q=process_queue)
    async.start()

    # Setting up session
    session['link_list'] = links
    session['company_list'] = company_list
    session['system_state'] = 'Idle'

    if not os.path.exists(config.RESULT_OUT_PATH):
        os.makedirs(config.RESULT_OUT_PATH)


@app.route('/')
def index():
    global initialised, driver, process_queue

    if 'error' in session.keys():
        session.pop('error')

    if 'info' in session.keys():
        session.pop('info')

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


@app.route('/get_next', methods=['POST'])
def getNext():
    global company_queue, process_queue, async
    if request.method == 'POST':
        next_n = int(request.form['next_n'])
        if company_queue is not None and isinstance(company_queue, NextQueue):
            session['system_state'] = 'Crawling'

            company_list = company_queue.getNext(next_n)
            links = []

            for company in company_list:
                try:
                    links.extend(crawler.getSearchUrls(company))
                except URLError:
                    session['error'] = 'Connection timeout'
                    return

            print links
            process_queue = ProcessQueue(links)

            async = Async(driver=driver, process_q=process_queue)
            async.start()

            session['link_list'] = links
            session['company_list'] = company_list
            session['system_state'] = 'Idle'

    return redirect('/')


@app.route('/load_url_list')
def loadURLList():
    global process_queue

    if not isinstance(process_queue, ProcessQueue):
        session['error'] = 'loadURLList > not a ProcessQueue'
        return redirect('/')

    file_handler = FileHandler(file_name=config.COMPANY_LIST_PATH)
    company_list = file_handler.read()

    links = []
    for company in company_list:
        links.extend(crawler.getSearchUrls(company))

    file_handler = FileHandler(file_name=config.LINK_LIST_PATH)
    file_handler.write(links)

    initSystem()

    return redirect('/')


if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True, port=5002)
