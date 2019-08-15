import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options


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
    locator_domain = 'http://frantones.com/'
    ext = 'Locations.html'
    driver = get_driver()
    driver.get(locator_domain + ext)
    all_store_data = []
    body = driver.find_elements_by_css_selector('table.blk12px')[1]
    tr = body.find_element_by_css_selector('tr')
    tds = tr.find_elements_by_css_selector('td')
    ps = tds[2].find_elements_by_css_selector('p')
    d_content = ps[0].text.split('\n')
    location_name = d_content[0]
    street_address = d_content[1]
    phone_number = d_content[4]

    lat = '<MISSING>'
    longit = '<MISSING>'
    country_code = 'US'
    location_type = '<MISSING>'
    store_number = '<MISSING>'
    hours = '<MISSING>'
    state = '<MISSING>'
    city = '<MISSING>'
    zip_code = '<MISSING>'

    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                  store_number, phone_number, location_type, lat, longit, hours]
    all_store_data.append(store_data)


    c_content = ps[1].text.split('\n')
    location_name = c_content[0]
    street_address = c_content[1]
    phone_number = c_content[4]
    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                  store_number, phone_number, location_type, lat, longit, hours]
    all_store_data.append(store_data)


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
