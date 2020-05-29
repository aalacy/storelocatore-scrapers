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
    locator_domain = 'https://www.pizzicatopizza.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('section#stores')
    cols = main.find_elements_by_css_selector('div.col.sqs-col-4.span-4')

    all_store_data = []
    for col in cols:
        stores = col.text.split('\n')
        i = 0
        while i < len(stores):
            location_name = stores[i]
            phone_number = stores[i + 1]
            street_address = stores[i + 2]
            if ',' not in stores[i + 3]:
                city, state, zip_code = addy_extractor('Portland, OR 97202')
            else:
                city, state, zip_code = addy_extractor(stores[i + 3])

            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            hours = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)
            i += 4

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
