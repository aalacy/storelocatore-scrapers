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
    state_zip = address[1].strip().split('  ')
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://tacohouse.org/'
    ext = 'About_Us.html'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    temp = []
    locs = driver.find_elements_by_css_selector('div.ColumnMarginBox')
    for loc in locs:
        content = loc.text.split('\n')
        temp.append(content)

    ext = 'Hours_of_Operation.html'
    driver.get(locator_domain + ext)

    hours_divs = driver.find_elements_by_css_selector('div.ColumnMarginBox')
    all_store_data = []
    for hours_d in hours_divs:
        content = hours_d.text.split('\n')
        for t in temp:
            if t[0] in content[0]:
                street_address = t[0]
                city, state, zip_code = addy_ext(t[2])
                phone_number = t[3]
                hours = content[2] + ' ' + content[3]

                country_code = 'US'
                location_name = '<MISSING>'
                store_number = '<MISSING>'
                location_type = '<MISSING>'
                lat = '<MISSING>'
                longit = '<MISSING>'
                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
