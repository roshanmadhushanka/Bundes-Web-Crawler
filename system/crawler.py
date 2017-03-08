import urllib2
from bs4 import BeautifulSoup
from flask import request


def getSearchUrls(company_name):
    '''
    Search for particular company name and get set of urls related to that company
    :param company_name: company name that needed to be searched
    :return: set of urls from the result
    '''

    search_url = 'https://www.bundesanzeiger.de/ebanzwww/wexsservlet?global_data.designmode=eb&genericsearch_param.fulltext=' \
                 + company_name + '&genericsearch_param.part_id=&%28page.navid%3Dto_quicksearchlist%29=Suchen'

    page = urllib2.urlopen(search_url)
    soup = BeautifulSoup(page, "lxml")
    table_result = soup.findAll("table", {"summary": "Trefferliste"})
    td_results = [a.find_all("td", {"class": "info"}) for a in table_result]

    if len(td_results) == 0:
        return

    available_links = []
    for p in td_results:
        for t in p:
            for a in t:
                result_url = 'https://www.bundesanzeiger.de/' + a['href']
                available_links.append(result_url)

    return available_links


def getSearchUrlsFromDriver(company_name, driver):
    '''
    Search for particular company name and get set of urls related to that company
    :param company_name: company name that needed to be searched
    :return: set of urls from the result
    '''

    driver.get('https://www.bundesanzeiger.de/ebanzwww/wexsservlet')

    captcha_input = driver.find_element_by_id("genericsearch_param.fulltext")
    captcha_input.send_keys(company_name)

    submit = driver.find_element_by_name("(page.navid=to_quicksearchlist)")
    submit.click()

    soup = BeautifulSoup(driver.page_source, "lxml")
    table_result = soup.findAll("table", {"summary": "Trefferliste"})
    td_results = [a.find_all("td", {"class": "info"}) for a in table_result]

    if len(td_results) == 0:
        return

    available_links = []
    for p in td_results:
        for t in p:
            for a in t:
                result_url = 'https://www.bundesanzeiger.de/' + a['href']
                available_links.append(result_url)

    return available_links


def getDocumentDetails(soup):
    if not isinstance(soup, BeautifulSoup):
        print 'crawler -> getDocumentDetails : Cannot foung BeautifulSoup instance'
        return

    name = soup.find("td", {"class": "first"}).text.strip()
    info = soup.find("td", {"class": "info"}).text.strip()
    preview_data = soup.find("div", {"id": "preview_data"}).prettify(encoding='utf-8')

    return {'name': name, 'info': info, 'preview_data': preview_data}