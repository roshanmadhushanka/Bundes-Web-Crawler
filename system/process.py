import threading
import time
import config
import crawler
import globals
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException
from system.io import FileHandler


class Async(threading.Thread):
    def __init__(self, process_q, driver):
        super(Async, self).__init__()
        self._stop = True
        self._condition = threading.Condition()
        self._process_q = process_q
        self._driver = driver

    def resume(self):
        # Resume thread execution from pause state
        with self._condition:
            self._stop = False
            self._condition.notify()

    def run(self):
        # Run process queue
        while True:
            _url = self._process_q.dequeue()
            if _url is None:
                break

            # Currently processing URL
            # globals.setCurrentURL(_url)

            while True:
                with self._condition:
                    if self._stop:
                        self._condition.wait()  # block until notified

                self._driver.get(_url)
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
                    _file_name = _doc_data['name'] + ' ' + _doc_data['info'] + '.html'
                    _html_string = '<html><body>' + _doc_data['preview_data'] + '</body></html>'

                    # Write result to file
                    file_handler = FileHandler(_file_name)
                    file_handler.write(_html_string)

                    # Increment process to global state
                    # globals.incrementIteration()

                    break
                except NoSuchElementException:
                    time.sleep(config.prop['SLEEP_TIME'])

    def pause(self):
        # Pause execution of process queue
        with self._condition:
            self._stop = True