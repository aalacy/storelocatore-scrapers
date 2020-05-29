import csv
import os
from sgselenium import SgSelenium
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://ca.longchamp.com/'
    ext = 'en/stores'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    stores = driver.find_elements_by_css_selector('li.bb-gray')
    link_list = []
    for store in stores:
        link = store.find_element_by_css_selector('a').get_attribute('href')
        link_list.append(link)

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)

        map_div = driver.find_element_by_css_selector('div#store-map')
        lat = map_div.get_attribute('data-lat')
        longit = map_div.get_attribute('data-lon')

        hours_html = driver.find_element_by_css_selector('div.js-to_expand.animated-expandmore').get_attribute(
            'innerHTML')

        hours = BeautifulSoup(hours_html, 'html.parser').text

        if 'Facebook' in hours:
            hours = '<MISSING>'
        else:
            hours = hours.replace('\n', ' ').strip()

        location_name = driver.find_element_by_css_selector('h2.title-gamma.upper.pt-1.pb-05').text
        cont = driver.find_element_by_css_selector(
            'div.ff-light.mt-05.mb-1.js-accordion.accordion--beta.accordion').text.split('\n')
        addy = cont[0].split(' ')
        street_address = ' '.join(addy[:-1])
        city = ' '.join(addy[-1:])
        phone_number = cont[-2]

        state = '<MISSING>'
        zip_code = '<MISSING>'
        country_code = 'CA'
        page_url = link
        store_number = '<MISSING>'
        location_type = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
