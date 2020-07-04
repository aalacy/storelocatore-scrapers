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
    locator_domain = 'http://singaspizzas.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    stores = driver.find_elements_by_css_selector('div.et_pb_text.et_pb_module.et_pb_text_align_left')

    all_store_data = []
    for store in stores:
        content = store.text.split('\n')

        if len(content) > 1:
            location_name = content[0]
            print(location_name)
            street_address = content[1]
            if "," not in content[2]:
                city = content[2]
                zip_code = content[3]
                phone_number = content[4]
                state = '<MISSING>'
            else:
                 cont=content[2].split(",")
                 city = cont[0]
                 cont=cont[1].strip().split(" ")
                 state=cont[0]
                 zip_code=cont[1]
                 phone_number = content[3]

            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            hours = '<MISSING>'
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
