import csv
import os
from sgselenium import SgSelenium

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
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'http://www.mccarthytire.com/'
    ext = 'Locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.execute_script('return locListings')

    all_store_data = []
    locations = driver.find_elements_by_css_selector('div.loclisting')
    for l in locations:
        location_name = \
        l.find_element_by_css_selector('p.subtitle').find_element_by_css_selector('strong').text.replace(
            'McCarthy Tire Service - ', '').split(',')[0].strip()
        for loc in locs:
            if loc['city'] == location_name:
                lat = loc['lat']
                longit = loc['lon']
                break

        if lat == 0.00:
            lat = '<MISSING>'
            longit = '<MISSING>'

        page_url = l.find_element_by_css_selector('a.DetailLink').get_attribute('href')
        addy = l.find_element_by_css_selector('div.locationInfo').text.split('\n')

        street_address = addy[2]

        city, state, zip_code = addy_ext(addy[3])

        hours = l.find_element_by_css_selector('div.locationhours').text.replace('Hours', '').replace('\n', ' ').strip()

        phone_number = l.find_element_by_css_selector('div.locphone').text

        country_code = 'US'

        location_type = '<MISSING>'

        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
