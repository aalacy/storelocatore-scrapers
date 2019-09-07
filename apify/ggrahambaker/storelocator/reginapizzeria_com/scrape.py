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


def fetch_data():
    locator_domain = 'http://reginapizzeria.com/'
    ext = 'southshore_plaza.html'

    driver = get_driver()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_xpath('//a[@class="dropdown-item"]')
    link_list = []
    for loc in locs:
        link_list.append(loc.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        divs = driver.find_elements_by_css_selector('div.mbr-article')

        addy = divs[0].text.split('\n')
        if 'Regina Pizz' in addy[0]:
            del addy[0]


        street_address = addy[0]
        city, state, zip_code = addy_ext(addy[1])

        phone_number = addy[2]
        if len(phone_number) > 13:
            phone_number = '<MISSING>'

        hours = divs[3].text.replace('\n', ' ')
        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        longit = '<MISSING>'
        lat = '<MISSING>'

        start_idx = link.find('.com/')
        location_name = link[start_idx + 5:].replace('.html', '').replace('_', ' ')

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
