import csv
import os
from sgselenium import SgSelenium
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'http://stores.redwing.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    countries = driver.find_elements_by_css_selector('a.cities')
    country_list = []
    for c in countries:
        country_list.append(c.get_attribute('href'))

    state_list = []

    for country in country_list:
        driver.get(country)
        driver.implicitly_wait(10)
        states = driver.find_elements_by_css_selector('a.cities')
        for s in states:
            state_list.append(s.get_attribute('href'))

    city_list = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        cities = driver.find_elements_by_css_selector('a.cities')
        for c in cities:
            city_list.append(c.get_attribute('href'))

    location_list = []

    for city in city_list:
        driver.get(city)
        driver.implicitly_wait(10)
        store_links = driver.find_elements_by_css_selector('a.website.pull-right')
        for link in store_links:
            location_list.append(link.get_attribute('href'))

    all_store_data = []
    for i, link in enumerate(location_list):
        driver.get(link)
        driver.implicitly_wait(10)

        loc_j = driver.find_elements_by_xpath('//script[@type="application/ld+json"]')
        loc_json = json.loads(loc_j[0].get_attribute('innerHTML'))

        location_name = loc_json['name']

        phone_number = loc_json['telephone']

        addy = loc_json['address']

        street_address = addy['streetAddress']
        city = addy['addressLocality']
        state = addy['addressRegion']
        zip_code = addy['postalCode']
        if len(zip_code.split(' ')) == 2:
            country_code = 'CA'
        else:
            country_code = 'US'

        geo = loc_json['geo']
        lat = geo['latitude']
        longit = geo['longitude']

        if 'openingHours' in loc_json:
            hours_list = loc_json['openingHours']
            hours = ''
            for h in hours_list:
                hours += h + ' '
            hours = hours.strip()
        else:
            hours = '<MISSING>'

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
