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

def addy_extractor(src):
    arr = src.split(',')
    city = arr[0]
    prov_zip = arr[1].strip().split(' ')
    state = prov_zip[0].strip()
    zip_code = prov_zip[1].strip()

    return city, state, zip_code

def fetch_data():
    # Your scraper here
    locator_domain = 'https://www.signatureny.com/'
    ext = 'contact/private-client-offices'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    tables = driver.find_elements_by_css_selector('table.table.table-striped.table-bordered')
    all_store_data = []

    for table in tables:
        rows = table.find_element_by_css_selector('tbody').find_elements_by_css_selector('tr')
        for row in rows:
            cols = row.find_elements_by_css_selector('td')
            address = cols[0].text.split('\n')
            if len(address) == 3:
                street_address = address[0] + ' ' + address[1]
                location_name = '<MISSING>'
                city, state, zip_code = addy_extractor(address[2])
            elif len(address) == 2:
                street_address = address[0]
                location_name = '<MISSING>'
                city, state, zip_code = addy_extractor(address[1])
            elif len(address) == 4:
                street_address = address[0]
                location_name = '<MISSING>'
                city, state, zip_code = addy_extractor(address[-1])
            elif len(address) == 6:
                country_code = 'US'
                store_number = '<MISSING>'
                phone_number = '<MISSING>'
                location_type = '<MISSING>'
                lat = '<MISSING>'
                longit = '<MISSING>'

                street_address = address[0]
                location_name = '<MISSING>'
                city, state, zip_code = addy_extractor(address[1])

                hours_arr = cols[2].text.split('\n')
                hours = hours_arr[0]

                store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                              store_number, phone_number, location_type, lat, longit, hours]
                all_store_data.append(store_data)

                street_address = address[4]
                location_type = address[3]
                city, state, zip_code = addy_extractor(address[5])

                hours_arr = cols[2].text.split('\n')
                hours = hours_arr[0]

            else:
                continue

            country_code = 'US'
            store_number = '<MISSING>'
            phone_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'

            hours_arr = cols[2].text.split('\n')
            hours = hours_arr[0]

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]

            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
