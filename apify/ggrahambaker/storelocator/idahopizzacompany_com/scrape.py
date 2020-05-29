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
    address = addy.split(',')
    city = address[0]
    state_zip = address[1].strip().split(' ')
    state = state_zip[0].replace('.', '')
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.idahopizzacompany.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    table = driver.find_element_by_css_selector('table#R_C_T_m_1598_ctl00_ctl00_dgItems')
    locs = table.find_elements_by_css_selector('tr')[1:]
    all_store_data = []
    for loc in locs:
        cont = loc.find_elements_by_css_selector('td')[0].text.split('\n')
        location_name = cont[0].split('.')[1].strip()
        street_address = cont[1]
        city, state, zip_code = addy_ext(cont[2])
        phone_number = cont[3]

        lat = '<MISSING>'
        longit = '<MISSING>'

        country_code = 'US'
        location_type = '<MISSING>'
        store_number = '<MISSING>'

        hours = 'SUNDAY-THURSDAY 11AM-10PM FRIDAY-SATURDAY 11AM-11PM Hours may vary at locations.'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
