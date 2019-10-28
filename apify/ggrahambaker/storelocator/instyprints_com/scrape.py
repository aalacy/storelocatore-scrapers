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
    locator_domain = 'https://www.instyprints.com/'
    ext = 'locations.html'

    driver = get_driver()
    driver.get(locator_domain + ext)

    hrefs = driver.find_elements_by_xpath("//a[contains(@href, 'instyprints.com/locations/')]")
    link_list = []
    for h in hrefs:
        link_list.append(h.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        loc_j = driver.find_element_by_xpath('//script[@type="application/ld+json"]')
        loc_json = json.loads(loc_j.get_attribute('innerHTML'))
        addy = loc_json['address']
        street_address = addy['streetAddress']
        city = addy['addressLocality']
        state = addy['addressRegion']
        zip_code = addy['postalCode']

        phone_number = loc_json['telephone']
        hours_arr = loc_json['openingHours']
        hours = ''
        for h in hours_arr:
            hours += h + ' '

        lat = loc_json['geo']['latitude']
        longit = loc_json['geo']['longitude']

        page_url = link
        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'
        location_name = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
