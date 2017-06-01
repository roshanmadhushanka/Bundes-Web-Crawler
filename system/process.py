import threading
import time
import config
import string
import pymongo
import system.crawler as crawler
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from system.io import FileHandler, MongoHandler


def extract_table_head(_table_head):
    # Tuple list
    _row_data = []

    # Table head rows
    _tr_list = _table_head.find_all(name='tr')
    for _tr_tag in _tr_list:
        # Extract th cols
        _col_data = []

        _th_list = _tr_tag.find_all(name='th')
        for _th_tag in _th_list:
            _th_tag = ' '.join(_th_tag.text.split())
            _col_data.append(_th_tag)

        if len(_col_data) > 0:
            _row_data.append(_col_data)

        # Extract td cols
        _td_cols = []
        _td_list = _tr_tag.find_all(name='td')
        for _td_tag in _td_list:
            _td_tag = ' '.join(_td_tag.text.split())
            _td_cols.append(_td_tag)

        if len(_td_cols) > 0:
            _row_data.append(_td_cols)

    return _row_data


def extract_table_body(_table_body):
    _row_data = []
    _tr_list = _table_body.find_all(name='tr')
    for _td_tag in _tr_list:
        # Extract col data
        _col_data = []
        _td_list = _td_tag.find_all(name='td')
        for _td_tag in _td_list:
            _td_tag = ' '.join(_td_tag.text.split())
            _col_data.append(_td_tag)

        if len(_col_data) > 0:
            _row_data.append(_col_data)

    return _row_data


def process(html_str):
    # Parse web page
    _soup = BeautifulSoup(html_str, "lxml")

    # Document data
    _document_data = {}

    # Extract title1
    _title1_tag = _soup.find(name='h3', attrs={'class': 'z_titel'})
    _title1 = ''
    if _title1_tag is not None:
        _title1 = ' '.join(_title1_tag.text.split())

    _document_data['title1'] = _title1

    # Extract title2
    _title2_tag = _soup.find(name='h4', attrs={'class': 'z_titel'})
    _title2 = ''
    if _title2_tag is not None:
        _title2 = ' '.join(_title2_tag.text.split())
    _document_data['title2'] = _title2

    # Extract title3
    _title3_tag = _soup.find(name='h3', attrs={'class': 'l_titel'})
    _title3 = ''
    if _title3_tag is not None:
        _title3 = ' '.join(_title3_tag.text.split())
    _document_data['title3'] = _title3

    # Extract table data
    _table_list = _soup.find_all(name='table', attrs={'class': 'std_table'})
    _tables = []
    for _table_tag in _table_list:
        _table_data = {}
        # Extract table head data
        _table_head = _table_tag.find(name='thead')
        if _table_head is not None:
            _thead = extract_table_head(_table_head)
            _table_data['thead'] = _thead

        _table_body = _table_tag.find(name='tbody')
        if _table_body is not None:
            _tbody = extract_table_body(_table_body)
            _table_data['tbody'] = _tbody

        _tables.append(_table_data)
    _document_data['tables'] = _tables

    # Extract paragraph data
    _p_list = _soup.find_all(name='p')
    _paragraph_data = []
    for _p_tag in _p_list:
        _paragraph_data.append(' '.join(_p_tag.text.split()))

    _paragraph_data = [x for x in _paragraph_data if (x.lower() != 'aktiva' and x.lower() != 'passiva' and x != '')]
    _document_data['paragraphs'] = _paragraph_data

    return _document_data


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
                    # _file_path = config.RESULT_OUT_PATH + _file_name + '.html'
                    # _file_handler = FileHandler(_file_path)
                    # _file_handler.write(_html_string)

                    try:
                        _db_handler = MongoHandler()
                        _document = process(_html_string)
                        _document['file_name'] = _file_name
                        _db_handler.insertDocument(_document)
                    except pymongo.errors.ServerSelectionTimeoutError:
                        print("Cannot connect to the database. Service timeout")
                    finally:
                        _db_handler.closeDatabaseClient()
                    break
                except NoSuchElementException:
                    time.sleep(config.SLEEP_TIME)
                except WebDriverException:
                    print("Browser has closed, terminate")
                    return
                except AttributeError:
                    break

    def pause(self):
        '''
        Pause process queue operations
        :return:
        '''
        # Pause execution of process queue
        with self._condition:
            self._stop = True

    def printDoc(self, _document_data):
        print(_document_data['title1'])
        print(_document_data['title2'])
        print(_document_data['title3'])
        print(_document_data['tables'])
        print(_document_data['paragraphs'])

