import csv
import os
from sgselenium import SgSelenium
from selenium.common.exceptions import NoSuchElementException

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
    if len(state_zip) == 3:
        state = state_zip[0] + ' ' + state_zip[1]
        zip_code = state_zip[2]
    else:
        state = state_zip[0]
        zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://giovannispizzapower.com/'
    ext = 'stores-sitemap.xml'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    links = driver.find_element_by_css_selector('tbody').find_elements_by_css_selector('tr')
    link_list = []
    for l in links:
        link_list.append(l.find_element_by_css_selector('td').find_element_by_css_selector('a').get_attribute('href'))

    all_store_data = []
    for i, link in enumerate(link_list):
        driver.get(link)
        driver.implicitly_wait(10)
        location_name = driver.find_element_by_css_selector('h1.entry-title').text

        lat = driver.find_element_by_css_selector('div#store_locator_single_map').get_attribute('data-lat')
        longit = driver.find_element_by_css_selector('div#store_locator_single_map').get_attribute('data-lng')

        addy = driver.find_element_by_css_selector('div.store_locator_single_address').text.replace('Address',
                                                                                                    '').strip().split(
            '\n')
        street_address = addy[0]
        city, state, zip_code = addy_ext(addy[1])

        phone_number = driver.find_element_by_css_selector(
            'div.store_locator_single_contact').find_element_by_css_selector('a').text

        try:
            hours = driver.find_element_by_css_selector('div.store_locator_single_opening_hours').text.replace(
            'Opening Hours', '').strip().replace('\n', ' ')

        except NoSuchElementException:
            hours = '<MISSING>'

        country_code = 'US'
        page_url = link
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        print(link)

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
