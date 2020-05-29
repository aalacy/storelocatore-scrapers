import csv
import os
from sgselenium import SgSelenium

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
    locator_domain = 'https://www.solidcore.co/'
    ext = 'studios/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    main = driver.find_element_by_css_selector('ul.list-locations')
    hrefs = main.find_elements_by_css_selector('a')

    link_list = []
    for href in hrefs:
        if len(href.get_attribute('href')) > 24:
            link_list.append(href.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(60)

        main = driver.find_element_by_css_selector('div.page-header.hero.hero-studio')
        if 'coming' in main.text:
            continue

        location_name = main.find_element_by_css_selector('h1').text.replace('\n', ' ')

        addy = main.find_element_by_css_selector('li.studio-address').text.split('\n')

        street_address = addy[0]
        city, state, zip_code = addy_ext(addy[1])

        phone_number = main.find_element_by_css_selector('li.studio-contact').text.split('\n')[0]

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        longit = '<MISSING>'
        lat = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
