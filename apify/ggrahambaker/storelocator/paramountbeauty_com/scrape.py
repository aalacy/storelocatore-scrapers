import csv
import os
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('paramountbeauty_com')



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
    locator_domain = 'https://www.paramountbeauty.com/'
    ext = 'Locator/?Store'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    result = driver.find_element_by_css_selector('ol.locator-results__list')
    stores = result.find_elements_by_css_selector('li.locator-results__item')

    all_store_data = []
    for store in stores:
        details = store.text.split('\n')
        logger.info(len(details))
        location_name = '<MISSING>'
        street_address = details[2]
        city, state, zip_code = addy_extractor(details[3])
        if len(details) > 5:
            phone_number = details[4]
            hours = details[5]
        else:
            phone_number = '<MISSING>'
            hours = '<MISSING>'

        country_code = 'US'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        store_number = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        logger.info(store_data)
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
