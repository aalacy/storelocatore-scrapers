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
    address = addy.split(' ')
    if len(address) == 4:
        city = address[0] + ' ' + address[1]
        state = address[2]
        zip_code = address[3]
    else:
        city = address[0]
        state = address[1]
        zip_code = address[2]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.texadelphia.com/'
    ext = 'locations-menu/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)
    driver.implicitly_wait(10)

    all_store_data = []
    div = driver.find_element_by_css_selector('ul.searchresults')
    stores = div.find_elements_by_css_selector('li')

    for store in stores:
        content = store.text.split('\n')

        if len(content) == 9:
            location_name = content[0]
            street_address = content[1]
            city, state, zip_code = addy_ext(content[2])
            phone_number = content[3].replace('T.', '').strip()
            hours = content[4] + ' ' + content[5]
        elif len(content) == 8:
            location_name = content[0]
            street_address = content[1]
            city, state, zip_code = addy_ext(content[2])
            phone_number = content[3].replace('T.', '').strip()
            hours = content[4]
        elif len(content) == 10:
            location_name = content[0]
            street_address = content[1]
            city, state, zip_code = addy_ext(content[2])
            phone_number = content[3].replace('T.', '').strip()
            hours = content[4] + ' ' + content[5] + ' ' + content[6]

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
