import csv
import os
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('mini-mart_com')



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
    locator_domain = 'http://mini-mart.com/'
    ext = 'locations.php'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    table = driver.find_element_by_css_selector('table')
    rows = table.find_elements_by_css_selector('tr')
    all_store_data = []
    for row in rows[1:]:
        logger.info(':)')
        cols = row.find_elements_by_css_selector('td')
        cont = cols[1].text.split('\n')
        location_name = cont[0]
        store_number_split = cont[0].split('#')
        if len(store_number_split) == 1:
            # no number 
            store_number = '<MISSING>'
            location_type = 'MINI MART HEADQUARTERS'
        else:
            store_number = store_number_split[1]
            location_type = 'STORE'

        street_address = cont[1]
        city, state, zip_code = addy_ext(cont[2])

        phone_number = cols[2].text.split('FAX')[0].replace('\n', '')
        
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'
        page_url = '<MISSING>'
        country_code = 'US'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
