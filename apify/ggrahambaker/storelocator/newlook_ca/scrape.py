import csv
import os
from sgselenium import SgSelenium
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('newlook_ca')



def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.newlook.ca/'
    ext = 'en/stores'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div.succrsales-list')
    locs = main.find_elements_by_css_selector('a.btn.btn-white-border')
    link_list = []
    for loc in locs:
        link_list.append(loc.get_attribute('href'))

    all_store_data = []
    for i, link in enumerate(link_list):
        driver.get(link)
        driver.implicitly_wait(10)
        logger.info(i)
        logger.info(link)
        cont = driver.find_element_by_css_selector('div.card-info').text.split('\n')

        location_name = cont[0]

        street_address = cont[1]

        off = 0

        if ')' not in cont[2]:
            off += 1

        city_state = cont[off + 2].split('(')
        city = city_state[0].strip()
        state = city_state[1].replace(')', '').strip()

        zip_code = cont[off + 3]

        phone_number = cont[off + 4].replace('T', '').strip()

        hours = driver.find_element_by_css_selector('ul.working-hours-list').text.replace('\n', ' ')

        lat = '<MISSING>'
        longit = '<MISSING>'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        country_code = 'CA'

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
