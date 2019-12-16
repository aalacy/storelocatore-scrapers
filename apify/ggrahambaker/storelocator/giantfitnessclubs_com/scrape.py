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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def fetch_data():
    locator_domain = 'https://giantfitnessclubs.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)

    stores = driver.find_elements_by_css_selector('div.column.mcb-column.one-fourth.column_column.column-margin-')
    link_list = []
    for store in stores:
        link_list.append(store.find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        print(link)
        driver.implicitly_wait(10)
        location_name = link[link.find('.com/') + 5:].replace('-', ' ').replace('/', '')

        divs = driver.find_elements_by_css_selector('div.column_attr.clearfix')
        for div in divs:
            print(div.text)
            if 'Address:' in div.text:
                content = div.text.split('/n')
        street_address = content[1]
        city, state, zip_code = addy_ext(content[2])
        phone_number = content[4].replace('Phone:', '').strip()
        hours = ''
        for h in content[7:]:
            hours += ' '.join(h.split()) + ' '

        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = link
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
