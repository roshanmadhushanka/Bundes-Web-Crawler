import threading
import time
import config
import string
import system.crawler as crawler
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from system.io import FileHandler

def extract_table_head(table_head):
    # Tuple list
    row_data = []

    # Table head rows
    tr_list = table_head.find_all(name='tr')
    for tr_tag in tr_list:
        # Extract th cols
        col_data = []

        th_list = tr_tag.find_all(name='th')
        for th_tag in th_list:
            th_tag = ' '.join(th_tag.text.split())
            col_data.append(th_tag)

        if len(col_data) > 0:
            row_data.append(col_data)

        # Extract td cols
        td_cols = []
        td_list = tr_tag.find_all(name='td')
        for td_tag in td_list:
            td_tag = ' '.join(td_tag.text.split())
            td_cols.append(td_tag)

        if len(td_cols) > 0:
            row_data.append(td_cols)

    return row_data


def extract_table_body(table_body):
    row_data = []
    tr_list = table_body.find_all(name='tr')
    for td_tag in tr_list:
        # Extract col data
        col_data = []
        td_list = td_tag.find_all(name='td')
        for td_tag in td_list:
            td_tag = ' '.join(td_tag.text.split())
            col_data.append(td_tag)

        if len(col_data) > 0:
            row_data.append(col_data)

    return row_data

def process(html_str):
    # Parse web page
    soup = BeautifulSoup(html_str, "lxml")

    # Document data
    document_data = {}

    # Extract title1
    title1_tag = soup.find(name='h3',
                           attrs={'class': 'z_titel', 'style': ' font-weight: bold; text-align: center;'})
    title1 = title1_tag.text.strip()
    document_data['title1'] = title1

    # Extract title2
    title2_tag = soup.find(name='h4',
                           attrs={'class': 'z_titel', 'style': ' font-weight: bold; text-align: center;'})
    title2 = title2_tag.text.strip()
    document_data['title2'] = title2

    # Extract title3
    title3_tag = soup.find(name='h3', attrs={'class': 'l_titel'})
    title3 = title3_tag.text.strip()
    document_data['title3'] = title3

    # Extract title4
    title4_tag = soup.find(name='h3', attrs={'class': 'b_teil'})
    title4 = title4_tag.text.strip()
    document_data['title4'] = title4

    # Extract table data
    table_list = soup.find_all(name='table', attrs={'class': 'std_table'})

    # List of tables in the document
    tables = []
    table_names = ['Aktiva', 'Passiva']

    isDocumentType2 = False

    for table in table_list:
        table_data = {}

        # Extract table title
        table_name = table_names.pop(0)
        table_data['name'] = table_name

        # Extract table headers
        table_headers = ['attribute']
        thead_tag_list = table.find_all(name='thead')

        for thead_tag in thead_tag_list:
            th_tag_list = thead_tag.find_all(name='th')

            if th_tag_list == []:
                # Document type 2
                isDocumentType2 = True

            # Extract table headers
            for th_tag in th_tag_list[2:]:
                th_text = ' '.join(th_tag.text.split())
                table_headers.append(th_text)

        # Add headers to table
        table_data['header'] = table_headers

        # Extract table data
        tbody = table.find(name='tbody')
        tr_tag_list = tbody.find_all(name='tr')
        row_data = []
        for tr_tag in tr_tag_list:
            keys = list(table_headers)
            data = []
            td_tag_list = tr_tag.find_all(name='td')
            for td_tag in td_tag_list:
                td_text = ' '.join(td_tag.text.split())
                data.append(td_text)
            row_data.append(data)

        if isDocumentType2:
            # If document type 2 detected
            index = 0
            for i in range(len(row_data)):
                if row_data[i][0] == 'Passiva':
                    index = i
                    break

            # Define table headers
            table_headers = row_data[index + 1]
            table_headers[0] = 'attribute'

            # Create two tables
            table1 = {'name': 'Aktiva', 'header': table_headers, 'data': row_data[:index]}
            table2 = {'name': 'Passiva', 'header': table_headers, 'data': row_data[index + 2:]}

            # Add generated tables to tables
            tables.append(table1)
            tables.append(table2)

            break

        # If not document type 2
        # Add table data to table
        table_data['data'] = row_data

        # Add table to tables
        tables.append(table_data)

    # Add tables to the document
    document_data['tables'] = tables

    # Generating text content
    text_content = {}

    # Extracting title of text content
    title5 = ""
    try:
        title5_tag = soup.find_all(name='h3', attrs={'class': 'b_teil'})[1]
        title5 = ' '.join(title5_tag.text.split())
    except IndexError:
        pass

    # Add title to text content
    text_content['title'] = title5

    # Extract contents
    contents = []
    p_tag_list = soup.find_all(name='p')

    index = 0
    if isDocumentType2:
        index = 2

    for p_tag in p_tag_list[index:]:
        data = ' '.join(p_tag.text.split())
        contents.append(data)

    # Add contents to text content
    text_content['content'] = contents

    # Add text content to the document
    document_data['text_content'] = text_content

    return document_data


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

                    _document = process(_html_string)
                    self.printDoc(_document)

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

    def printDoc(self, document_data):
        _tables = document_data['tables']
        _text = document_data['text_content']

        for _table in _tables:
            print(_table['name'])
            print("-----------------")

            print(_table['header'])
            for _line in _table['data']:
                print(_line)

        print(_text['title'])
        print("-----------")
        for _line in _text['content']:
            print(_line)
