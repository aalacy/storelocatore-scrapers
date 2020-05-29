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

def fetch_data():
    locator_domain = 'https://www.somersettrust.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locations = driver.execute_script('return locationsObject')
    all_store_data = []
    for loc in locations:
        city = loc['city']
        location_type = ''
        if loc['isATM'] == 1:
            location_type += 'ATM' + ' '
        if loc['isBranch'] == 1:
            location_type += 'Branch' + ' '

        location_type = location_type.strip()

        lat = loc['latitude']
        longit = loc['longitude']
        if '12340' in lat:
            lat = lat.replace('12340', '40')

        location_name = loc['name']
        phone_number = loc['phone'].replace('\xa0', '')

        if phone_number == '':
            phone_number = '<MISSING>'

        state = loc['state']
        street_address = loc['streetAddress'].replace('\xa0', '')
        zip_code = loc['zip']

        country_code = 'US'
        store_number = '<MISSING>'
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
