import os
from urllib2 import URLError

from flask import Flask, render_template, redirect, session, request
from flask_cors import CORS
from selenium import webdriver

import config
from system import crawler
from system.io import FileHandler
from system.process import Async
from system.structure import ProcessQueue, NextQueue
import sys
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

# Server upload
ALLOWED_EXTENSIONS = set(['txt'])


def isAllowed(file_name):
    global ALLOWED_EXTENSIONS
    return '.' in file_name and file_name.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def initSystem():
    global process_queue, driver, async, company_queue

    # Initialising variables
    # Retrieve
    file_handler = FileHandler(file_name=config.COMPANY_LIST_PATH)
    company_list = file_handler.read()
    company_list = [a.decode('utf-8') for a in company_list]

    if company_list is None:
        session['error'] = 'Company list cannot be found'
        return

    # Load company list to  the next queue
    company_queue = NextQueue(company_list)

    # Selenium Firefox driver
    driver = webdriver.Firefox(executable_path=config.GECKODRIVER_PATH)
    driver.start_client()

    # Setting up session

    session['company_list'] = company_list
    session['system_state'] = 'Idle'

    if not os.path.exists(config.RESULT_OUT_PATH):
        os.makedirs(config.RESULT_OUT_PATH)

    if not os.path.exists(config.DATABASE_PATH):
        os.makedirs(config.DATABASE_PATH)

    reload(sys)
    sys.setdefaultencoding('utf-8')


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

    if async is not None:
        print "Server :", "Running"
        session['system_state'] = 'Running'
        async.resume()

    return redirect('/')


@app.route('/stop_process')
def stopProcess():
    global async, driver

    if async is not None:
        print "Server :", "Idle"
        session['system_state'] = 'Idle'
        async.pause()

    return redirect('/')


@app.route('/get_next', methods=['POST'])
def getNext():
    # Load company list partially
    global company_queue, process_queue, async, driver

    if request.method == 'POST':
        next_n = int(request.form['next_n'])

        if company_queue is not None and isinstance(company_queue, NextQueue):
            session['system_state'] = 'Crawling'

            # Crawl company list
            company_list = company_queue.getNext(next_n)
            links = []
            for company in company_list:
                try:
                    links.extend(crawler.getSearchUrls(company))
                except URLError:
                    session['error'] = 'Connection timeout'
                    return

            # Create new process queue
            process_queue = ProcessQueue(links)

            if async is not None:
                # Stop previous queue process
                async.pause()

            # Initiate new queue process
            async = Async(driver=driver, process_q=process_queue)
            async.start()

            # Set sessions
            session['link_list'] = links
            session['company_list'] = company_list
            session['system_state'] = 'Idle'

    return redirect('/')


@app.route('/load_url_list')
def loadURLList():
    # Load entire company list at once and generate link list
    global process_queue, async, driver

    file_handler = FileHandler(file_name=config.COMPANY_LIST_PATH)
    company_list = file_handler.read()

    links = []
    for company in company_list:
        links.extend(crawler.getSearchUrlsFromDriver(company, driver))

    file_handler = FileHandler(file_name=config.LINK_LIST_PATH)
    file_handler.write(links)

    # Create new process queue
    process_queue = ProcessQueue(links)

    if async is not None:
        # Stop previous queue process
        async.pause()

    # Initiate new queue process
    async = Async(driver=driver, process_q=process_queue)
    async.start()

    session['link_list'] = links
    session['company_list'] = company_list
    session['system_state'] = 'Idle'

    return redirect('/')


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global company_queue
    # Upload files to the server
    if request.method == 'POST':
        file = request.files['file']
        if file and isAllowed(file.filename):
            # Save uploaded data
            file_name = 'company.txt'
            file.save(os.path.join(config.DATABASE_PATH, file_name))

            # Read uploaded data
            file_path = config.DATABASE_PATH + file_name
            file_handler = FileHandler(file_path)
            content = file_handler.read()

            # Read company list
            file_handler = FileHandler(config.COMPANY_LIST_PATH)
            company_list = file_handler.read()

            # Extend company list with uploaded values
            company_list.extend(content)

            # Filter unique values
            company_list = list(set(company_list))

            # Save company list
            file_handler.write(company_list)

            # Load company list to  the next queue
            company_queue = NextQueue(company_list)

            # Set session
            session['company_list'] = company_list

    return redirect('/')

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.jinja_env.cache = {}
    app.run(debug=True, port=5002)
