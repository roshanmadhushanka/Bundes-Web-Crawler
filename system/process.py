import threading
import time
import config
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException



class Async(threading.Thread):
    def __init__(self, process_q, driver):
        super(Async, self).__init__()
        self._stop = True
        self._condition = threading.Condition()
        self._process_q = process_q
        self._driver = driver


    def resume(self):
        with self._condition:
            self._stop = False
            self._condition.notify()

    def run(self):
        # self.resume()
        while True:
            # with self._condition:
            #     if self._stop:
            #         self._condition.wait()  # block until notified
            # do stuff
            url = self._process_q.dequeue()
            if url is None:
                break

            while True:
                with self._condition:
                    if self._stop:
                        self._condition.wait()  # block until notified

                self._driver.get(url)
                try:
                    input_element = self._driver.find_element_by_id("captcha_data.solution")
                    input_element.send_keys('')
                except NoSuchElementException:
                    pass

                try:
                    element = self._driver.find_element_by_id("begin_pub")
                    soup = BeautifulSoup(self._driver.page_source, "lxml")
                    print soup.prettify()
                    break
                except NoSuchElementException:
                    time.sleep(config.prop['SLEEP_TIME'])

    def pause(self):
        with self._condition:
            self._stop = True

    def process(self):
        _url = self._process_q.dequeue()
        if _url is None:
            return
        self._driver.get(_url)
        try:
            input_element = self._driver.find_element_by_id("captcha_data.solution")
            input_element.send_keys('')
        except NoSuchElementException:
            pass

        try:
            element = self._driver.find_element_by_id("begin_pub")
            soup = BeautifulSoup(self._driver.page_source, "lxml")
            print soup.prettify()
        except NoSuchElementException:
            time.sleep(config.prop['SLEEP_TIME'])