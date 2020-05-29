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
    state = state_zip[0]
    zip_code = state_zip[1]
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.rostituscankitchen.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    main = driver.find_element_by_css_selector('div.footer-top')

    cont = main.find_elements_by_css_selector('div.widget-inner')[1].text.split('\n')

    spin = 0
    all_store_data = []
    for c in cont:
        if spin == 0:
            location_name = c
        elif spin == 1:
            street_address = c
        elif spin == 2:
            city, state, zip_code = addy_ext(c)
        else:
            phone_number = c

            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            lat = '<MISSING>'
            longit = '<MISSING>'
            hours = '<MISSING>'
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)
            spin = 0
            continue

        spin += 1

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
