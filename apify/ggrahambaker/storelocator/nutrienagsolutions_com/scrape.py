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
    locator_domain = 'https://www.nutrienagsolutions.com/'
    ext = 'find-location'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    data_list = driver.execute_script('return mapdata_ca')

    all_store_data = []
    for data in data_list:
        street_address = data['a']
        city = data['c'].strip()
        state = data['s'].strip()
        zip_code = data['z'].strip()
        if len(zip_code) < 5:
            zip_code = '<MISSING>'
        elif len(zip_code) == 6:
            #print(zip_code)
            zip_code = zip_code[0:3] + ' ' + zip_code[3:]
            #print(zip_code)

        if len(zip_code.split(' ')) == 2:
            country_code = 'CA'
        else:
            country_code = 'US'

        if 'S' in data['b']:
            store_info = data['b']['S'][0]
        elif 'O' in data['b']:
            store_info = data['b']['O'][0]

        store_number = store_info['no']
        phone_number = store_info['p']
        if phone_number == '':
            phone_number = '<MISSING>'
        location_type = store_info['l']
        location_name = store_info['n']
        lat = data['ln']
        longit = data['lt']
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
