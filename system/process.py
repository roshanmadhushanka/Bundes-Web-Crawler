import threading
import time
import config
import string
import system.crawler as crawler
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from system.io import FileHandler

class Async(threading.Thread):
    def __init__(self, process_q, driver):
        super(Async, self).__init__()
        self._stop = True
        self._condition = threading.Condition()
        self._process_q = process_q
        self._driver = driver

    def resume(self):
        '''
        Resume process queue operations
        :return: None
        '''
        # Resume thread execution from pause state
        with self._condition:
            self._stop = False
            self._condition.notify()

    def run(self):
        '''
        Initiate process queue execution
        :return: None
        '''
        # Run process queue
        while True:
            _url = self._process_q.dequeue()
            if _url is None:
                break

            while True:
                with self._condition:
                    if self._stop:
                        self._condition.wait()  # block until notified

                try:
                    self._driver.get(_url)
                except WebDriverException:
                    print("Browser has closed, terminate")
                    return

                try:
                    _input_element = self._driver.find_element_by_id("captcha_data.solution")
                    _input_element.send_keys('')
                except NoSuchElementException:
                    pass

                try:
                    # Raise an exception if 'begin_pub' element (result page) is not found
                    _element = self._driver.find_element_by_id("begin_pub")
                    _soup = BeautifulSoup(self._driver.page_source, "lxml")

                    # Parse document data
                    _doc_data = crawler.getDocumentDetails(_soup)
                    _html_string = '<html><body>' + _doc_data['preview_data'].decode('utf-8') + '</body></html>'

                    # Write result to file
                    _file_name = _doc_data['name'] + ' ' + _doc_data['info']
                    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
                    _file_name = ''.join(c for c in _file_name if c in valid_chars)
                    _file_path = config.RESULT_OUT_PATH + _file_name + '.html'
                    file_handler = FileHandler(_file_path)
                    file_handler.write(_html_string)

                    break
                except NoSuchElementException:
                    time.sleep(config.SLEEP_TIME)
                except WebDriverException:
                    print("Browser has closed, terminate")
                    return

    def pause(self):
        '''
        Pause process queue operations
        :return:
        '''
        # Pause execution of process queue
        with self._condition:
            self._stop = True