import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

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


def fetch_data():
    locator_domain = 'https://www.511tactical.com/'
    ext = 'store-locator'

    driver = get_driver()
    driver.get(locator_domain + ext)

    element = driver.find_elements_by_xpath('//button[@data-click="close"]')
    if len(element) != 0:
        driver.execute_script("arguments[0].click();", element[0])



    stores = driver.find_elements_by_css_selector('div.info-location')
    # 58
    link_list = []
    for store in stores:
        a_tag = store.find_elements_by_css_selector('a')
        if len(a_tag) == 0:
            continue

        a_tag = store.find_element_by_css_selector('a')
        href = a_tag.get_attribute('href')

        if re.search('^\d{5}?$', href[-5:]):
            if 'gurnee' in href:
                href = href[:-1]
            location_name = a_tag.text

            address = store.find_element_by_css_selector('address').text.split('\n')
            info = store.find_element_by_css_selector('p').text.split('\n')
            street_address = address[0]
            city, state, zip_code = addy_ext(address[1])
            phone_number = info[0]
            hours = ''
            for h in info[1:]:
                hours += h + ' '

            hours = hours.strip()
            store_info = [street_address, city, state, zip_code, phone_number, hours, location_name]
            link_list.append([href, store_info])

    all_store_data = []
    for link in link_list:
        driver.get(link[0])
        driver.implicitly_wait(10)

        content = driver.find_element_by_css_selector('div.location-details').text.split('\n')
        geo_idx = content.index('GEO')

        coords = content[geo_idx + 1].split(',')
        lat = coords[0]
        longit = coords[1]

        street_address = link[1][0]
        city = link[1][1]
        state = link[1][2]
        zip_code = link[1][3]
        phone_number = link[1][4]
        hours = link[1][5]
        location_name = link[1][6]
        if 'PORTLAN' in location_name:
            lat = '45.384869'
        if 'ALAMO' in location_name:
            lat = '<MISSING>'
            longit = '<MISSING>'

        country_code = 'US'
        location_type = '<MISSING>'
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
