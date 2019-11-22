import csv
import os
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup


def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://us.longchamp.com/'
    ext = 'stores'

    driver = get_driver()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    stores = driver.find_elements_by_css_selector('li.bb-gray')
    link_list = []
    for store in stores:
        link = store.find_element_by_css_selector('a').get_attribute('href')
        link_list.append(link)

    all_store_data = []
    for link in link_list:
        print(link)
        driver.get(link)
        driver.implicitly_wait(10)
        try:
            map_div = driver.find_element_by_css_selector('div#store-map')
        except NoSuchElementException:
            ## broken link
            continue
        lat = map_div.get_attribute('data-lat')
        longit = map_div.get_attribute('data-lon')
        if lat == '':
            lat = '<MISSING>'
        if longit == '':
            longit = '<MISSING>'


        hours_html = driver.find_element_by_css_selector('div.js-to_expand.animated-expandmore').get_attribute(
            'innerHTML')

        hours = BeautifulSoup(hours_html, 'html.parser').text

        if 'Facebook' in hours:
            hours = '<MISSING>'
        else:
            hours = hours.replace('\n', ' ').strip()


        location_name = driver.find_element_by_css_selector('h2.title-gamma.upper.pt-1.pb-05').text
        cont = driver.find_element_by_css_selector(
            'div.ff-light.mt-05.mb-1.js-accordion.accordion--beta.accordion').text.split('\n')

        street_address = cont[0]
        phone_number = cont[-2].replace('(','').replace(')', '').replace('+1', '').replace('+', '')


        city = '<MISSING>'
        state = '<MISSING>'
        zip_code = '<MISSING>'
        country_code = 'US'
        page_url = link
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        print()
        print(store_data)
        print()
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
