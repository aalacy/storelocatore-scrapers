import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

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
    prov_zip = arr[1].split(' ')
    if len(prov_zip) == 3:
        state = prov_zip[1].replace('.', '')
        zip_code = prov_zip[2]

    return city, state, zip_code




def fetch_data():
    locator_domain = 'https://www.directtoolsoutlet.com/'
    ext = 'locations/'

    driver = get_driver()
    driver.get(locator_domain + ext)
    time.sleep(5)
    driver.implicitly_wait(30)


    locations = driver.find_element_by_css_selector('ul.store-locations-list')
    links = locations.find_elements_by_css_selector('a.store-locations-list-link')
    link_list = []
    for l in links:
        link_list.append(l.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.implicitly_wait(10)
        driver.get(link)
        contact_info = driver.find_element_by_css_selector('div.module-locations-contacts-info')
        location_name = contact_info.find_element_by_css_selector('h2.module-locations-list-info-title').text

        address = contact_info.find_element_by_css_selector('address.module-locations-list-info-addr').text.split('\n')

        if len(address) == 2:
            street_address = address[0]
            city, state, zip_code = addy_extractor(address[1])
        elif len(address) == 3:
            street_address = address[0] + ' ' + address[1]
            city, state, zip_code = addy_extractor(address[2])

        phone_number = contact_info.find_element_by_css_selector('div.module-locations-list-info-phone').text


        hours = contact_info.find_element_by_css_selector('div.module-locations-list-info-hours').text.replace('\n', ' ').replace('Store Hours', '').strip()
        href = contact_info.find_element_by_xpath("//a[@title='Get Directions']").get_attribute('href')

        start_idx = href.find('n/')
        coords = href[start_idx + 2:].split(',')
        lat = coords[0]
        longit = coords[1]


        country_code = 'US'
        store_number = '<MISSING>'
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
