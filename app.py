from flask import Flask, render_template, redirect, request, url_for, session, send_from_directory
from flask_cors import CORS
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from system.io import FileHandler
from system import crawler
from system.structure import ProcessQueue
import time
from bs4 import BeautifulSoup

# Company list
company_list = []
company_list_updated = False

# Process queue
process_queue = ProcessQueue()

# Driver
driver = webdriver.Firefox(executable_path='C:\Users\Roshan\PycharmProjects\\bundesanzeiger\driver\geckodriver.exe')


def updateCompany():
    global company_list, company_list_updated
    file_handler = FileHandler(file_name='company_list')
    company_list = file_handler.read()
    company_list_updated = True
    updateProcessQueue()


def updateProcessQueue():
    global process_queue, company_list, driver
    if not isinstance(process_queue, ProcessQueue):
        return

    links = []
    for company in company_list:
        links.extend(crawler.getSearchUrls(company))

    process_queue.enqueue(links)

updateCompany()
updateProcessQueue()

while True:
    url = process_queue.dequeue()
    if url is None:
        break

    while True:
        driver.get(url)
        try:
            inputElement = driver.find_element_by_id("captcha_data.solution")
            inputElement.send_keys('')
        except NoSuchElementException:
            pass

        try:
            element = driver.find_element_by_id("begin_pub")
            soup = BeautifulSoup(driver.page_source, "lxml")
            print soup.prettify()
            break
        except NoSuchElementException:
            time.sleep(10)
