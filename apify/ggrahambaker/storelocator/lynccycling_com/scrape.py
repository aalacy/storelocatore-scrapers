import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
    locator_domain = 'https://www.lynccycling.com/'
    ext = 'say-hello'

    driver = get_driver()
    driver.get(locator_domain + ext)

    all_store_data = []
    locs = driver.find_elements_by_css_selector('div.vcard')
    for loc in locs:
        location_name = loc.find_element_by_css_selector('span.city').text
        street_address = loc.find_element_by_css_selector('div.street-address').text
        city = loc.find_element_by_css_selector('span.locality').text
        state = loc.find_element_by_css_selector('span.region').text
        zip_code = loc.find_element_by_css_selector('span.postal-code').text
        phone_number = loc.find_element_by_css_selector('div.phone').find_elements_by_css_selector('a')[1].text

        country_code = 'US'

        location_type = '<MISSING>'
        page_url = '<MISSING>'
        hours = '<MISSING>'
        longit = '<MISSING>'
        lat = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
