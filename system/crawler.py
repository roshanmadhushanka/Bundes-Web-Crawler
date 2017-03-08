import urllib2
from bs4 import BeautifulSoup
from flask import request


def getSearchUrls(company_name):
    '''
    Search for particular company name and get set of urls related to that company
    :param company_name: company name that needed to be searched
    :return: set of urls from the result
    '''

    _search_url = 'https://www.bundesanzeiger.de/ebanzwww/wexsservlet?global_data.designmode=eb&genericsearch_param.fulltext=' \
                 + company_name + '&genericsearch_param.part_id=&%28page.navid%3Dto_quicksearchlist%29=Suchen'

    _page = urllib2.urlopen(_search_url)
    _soup = BeautifulSoup(_page, "lxml")
    _table_result = _soup.findAll("table", {"summary": "Trefferliste"})
    _td_results = [a.find_all("td", {"class": "info"}) for a in _table_result]

    if len(_td_results) == 0:
        return

    _available_links = []
    for p in _td_results:
        for t in p:
            for a in t:
                _result_url = 'https://www.bundesanzeiger.de/' + a['href']
                _available_links.append(_result_url)

    return _available_links


def getSearchUrlsFromDriver(company_name, driver):
    '''
    Search for particular company name and get set of urls related to that company
    :param company_name: company name that needed to be searched
    :return: set of urls from the result
    '''

    driver.get('https://www.bundesanzeiger.de/ebanzwww/wexsservlet')

    _captcha_input = driver.find_element_by_id("genericsearch_param.fulltext")
    _captcha_input.send_keys(company_name)

    _submit = driver.find_element_by_name("(page.navid=to_quicksearchlist)")
    _submit.click()

    _soup = BeautifulSoup(driver.page_source, "lxml")
    _table_result = _soup.findAll("table", {"summary": "Trefferliste"})
    _td_results = [a.find_all("td", {"class": "info"}) for a in _table_result]

    if len(_td_results) == 0:
        return

    _available_links = []
    for p in _td_results:
        for t in p:
            for a in t:
                result_url = 'https://www.bundesanzeiger.de/' + a['href']
                _available_links.append(result_url)

    return _available_links


def getDocumentDetails(soup):
    if not isinstance(soup, BeautifulSoup):
        print 'crawler -> getDocumentDetails : Cannot foung BeautifulSoup instance'
        return

    _name = soup.find("td", {"class": "first"}).text.strip()
    _info = soup.find("td", {"class": "info"}).text.strip()
    _preview_data = soup.find("div", {"id": "preview_data"}).prettify(encoding='utf-8')

    return {'name': _name, 'info': _info, 'preview_data': _preview_data}