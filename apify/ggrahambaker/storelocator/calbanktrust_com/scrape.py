import csv
import os
from sgselenium import SgSelenium
import re

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
    state_zip = address[1].split(' ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    all_store_data = []
    locator_domain = 'https://www.calbanktrust.com/'
    ext = 'locations/'
    locations = ['san fransisco', 'los angeles', 'san diego', 'sacramento', 'fresno']

    for loc in locations:
        driver = SgSelenium().chrome()
        driver.get(locator_domain + ext)

        search_bar = driver.find_element_by_css_selector('input#bLocatorAddress')
        search_bar.clear()
        search_bar.send_keys(loc)
        button = driver.find_element_by_css_selector('button#bLocatorSearchButton')
        button.click()
        driver.implicitly_wait(60)

        locs = driver.find_elements_by_css_selector('div.list-group-item.hover-content.google_locations')
        for loc in locs:
            location_name = loc.find_element_by_css_selector('div.branch-name').text[3:]
            lines = loc.find_element_by_css_selector('div.branch-address').text.split('\n')
            street_address = lines[0]
            city, state, zip_code = addy_ext(lines[1])

            features = loc.find_element_by_css_selector('div.branch-features')
            divs = features.find_elements_by_css_selector('div.row')
            phone_number = divs[0].text.replace('Phone Number', '').strip()
            hours = ''

            hours += divs[2].text.strip() + ' '
            hours += divs[-2].text.strip()
            if 'Email' in hours:
                idx = hours.find('Email')
                hours = hours[:idx]

            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

        driver.quit()

    no_dup_data = []
    track_arr = []
    for data in all_store_data:
        if data[1] not in track_arr:
            no_dup_data.append(data)
            track_arr.append(data[1])

    return no_dup_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
