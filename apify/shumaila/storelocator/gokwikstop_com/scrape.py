import requests
from bs4 import BeautifulSoup
import csv
import string
import re, time
import usaddress
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('gokwikstop_com')





def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    chrome_path = '/Users/Dell/local/chromedriver'
    #return webdriver.Chrome(chrome_path, chrome_options=options)
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    data = []
    url = 'https://gokwikstop.com/store-locator/'
    driver = get_driver()
    driver.get(url)
    option = driver.find_element_by_xpath("//div[@id='wpsl-stores']/ul")
    listt = option.find_elements_by_css_selector('li')


    for llist in listt:
        store = llist.get_attribute('data-store-id')
        detail = llist.text
        detail = detail.replace("\n","|")
        logger.info(store)
        logger.info(detail)
        start = 0
        end = detail.find("|",start)
        title = detail[start:end]
        start = end + 1
        end = detail.find("|", start)
        street = detail[start:end]
        start = end + 1
        end = detail.find(" ", start)
        city = detail[start:end]
        start = end + 1
        end = detail.find(" ", start)
        state = detail[start:end]
        start = end + 1
        end = detail.find("|", start)
        pcode = detail[start:end]

        logger.info("......................................")

        data.append([
            url,
            title,
            street,
            city,
            state,
            pcode,
            "US",
            store,
            "<INACCESSIBLE>",
            "<MISSING>",
            "<MISSING>",
            "<MISSING>",
            "<MISSING>"
        ])
    driver.quit()
    return data


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
