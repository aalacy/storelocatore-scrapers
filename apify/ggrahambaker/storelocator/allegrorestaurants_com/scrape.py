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
    locator_domain = 'http://allegrorestaurants.com/'

    driver = get_driver()
    driver.get(locator_domain)

    hrefs = driver.find_elements_by_css_selector('a.heading-link')
    link_list = [hrefs[0].get_attribute('href'), hrefs[1].get_attribute('href')]

    all_store_data = []
    for link in link_list:
        driver.implicitly_wait(10)
        driver.get(link)

        content = driver.find_elements_by_css_selector('div.fusion-text')[1].text.split('\n')
        location_name = '<MISSING>'
        street_address = content[1]
        address = content[2].split(' ')
        if len(address) == 4:
            city = address[0] + ' ' + address[1]
            state = address[2]
            zip_code = address[3]
        else:
            city = address[0]
            state = address[1]
            zip_code = address[2]

        phone_number = content[4]
        hours = ''
        for h in content[6:]:
            hours += h + ' '
        hours = hours.strip()

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
