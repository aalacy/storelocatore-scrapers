import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome('chromedriver', options=options)


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
    locator_domain = 'https://www.brendans.com/'

    driver = get_driver()
    driver.get(locator_domain)

    hrefs = driver.find_elements_by_css_selector('a.image-slide-anchor.content-fill')
    link_list = []
    for href in hrefs:
        link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:

        print(link)
        print()
        print()
        driver.implicitly_wait(10)
        driver.get(link)
        map_element = driver.find_element_by_css_selector('div.sqs-block.map-block.sqs-block-map')
        json_addy_to = map_element.get_attribute('data-block-json')
        json_addy = json.loads(json_addy_to)

        street_address = json_addy['location']['addressLine1']

        address = json_addy['location']['addressLine2'].split(', ')
        city = address[0]
        state = address[1]
        zip_code = address[2]

        lat = json_addy['location']['markerLat']

        longit = json_addy['location']['markerLng']

        ps = driver.find_elements_by_css_selector('div.sqs-block-content')[3].find_elements_by_css_selector('p')

        phone_number = ps[1].find_element_by_css_selector('strong').text

        hours = ps[2].text.replace('\n', ' ')

        country_code = 'US'
        store_number = '<MISSING>'
        location_name = link[link.find('m/') + 2: ].replace('-', ' ')
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
