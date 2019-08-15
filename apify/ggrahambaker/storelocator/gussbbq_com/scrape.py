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


def addy_ext(addy):
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code


def loc_ext(driver, locator_domain, ext, all_store_data):
    link = ext[0]
    ids = ext[1]
    driver.get(locator_domain + link)
    driver.implicitly_wait(10)
    address = driver.find_element_by_css_selector('div' + ids[0]).text.split('\n')
    street_address = address[1]
    city, state, zip_code = addy_ext(address[2])
    phone_number = address[3]

    hours = driver.find_element_by_css_selector('div' + ids[1]).text.replace('\n', ' ').replace('HOURS', '').strip()

    lat = '<MISSING>'
    longit = '<MISSING>'
    location_name = '<MISSING>'
    country_code = 'US'
    location_type = '<MISSING>'
    store_number = '<MISSING>'
    store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                  store_number, phone_number, location_type, lat, longit, hours]
    all_store_data.append(store_data)


def fetch_data():
    locator_domain = 'https://www.gussbbq.com/'
    exts = [['claremont-lunch-dinner.html', ['#u144292-13', '#u144271-12']],
            ['southpasadena-lunch-dinner.html', ['#u143184-14', '#u143145-12']]]
    driver = get_driver()
    all_store_data = []
    for ext in exts:
        loc_ext(driver, locator_domain, ext, all_store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
