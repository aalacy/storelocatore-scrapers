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


def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code



def fetch_data():
    locator_domain = 'https://www.ycmc.com/'
    ext = 'locator'

    driver = get_driver()
    driver.get(locator_domain + ext)

    pop_up = driver.find_element_by_xpath("//a[@title='Close']")
    driver.execute_script("arguments[0].click();", pop_up)

    divs = driver.find_elements_by_css_selector('div.ycmc_store_detail')

    all_store_data = []
    for div in divs:
        content = div.text.split('\n')
        if len(content) == 1:
            continue

        location_name = content[0]
        street_address = content[1]
        city, state, zip_code = addy_extractor(content[2])
        phone_number = content[3].replace('Phone:', '').strip()
        hours = content[5] + ' ' + content[6]

        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
