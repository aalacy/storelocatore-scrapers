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
    locator_domain = 'https://jjsgrill.com/'
    ext = 'our-locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.container')
    atags = main.find_elements_by_css_selector('a')

    link_list = []
    for tag in atags:
        link_list.append(tag.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        location_name = driver.find_element_by_css_selector('h3.location_hdr').text
        addy = driver.find_element_by_css_selector('p.location_address').text.split('\n')

        street_address = addy[0]
        if '1 PRAIRIE CREEK MARINA' in street_address:
            city = 'ROGERS'
            state = 'AR'
            zip_code = '<MISSING>'
        elif '12111 W MARKHAM ST' in street_address:
            city = 'LITTLE ROCK'
            state = 'ARKANSAS'
            zip_code = '<MISSING>'
        elif '5320 WEST SUNSET AVE SUITE 184' in street_address:
            city = 'SPRINGDALE'
            state = 'ARKANSAS'
            zip_code = '<MISSING>'
        else:
            city, state, zip_code = addy_ext(addy[1])

        phone_number = driver.find_element_by_css_selector('p.location_phone').text
        hours = driver.find_element_by_css_selector('p.location_hours').text

        hours = hours.replace('DRANKS ‘TIL WE’RE CLOSED', '').strip()
        # lat = driver.find_element_by_css_selector('div.marker').get_attribute('data-lat')
        # longit = driver.find_element_by_css_selector('div.marker').get_attribute('data-lng')
        lat = '<MISSING>'
        longit = '<MISSING>'

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
