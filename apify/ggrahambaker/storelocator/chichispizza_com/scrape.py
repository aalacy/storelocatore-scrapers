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
    # Your scraper here
    locator_domain = 'https://www.chichispizza.com/'
    ext = 'locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    hours_div = driver.find_element_by_css_selector('div#WRchTxt2-hrv')

    hours = ''
    for h in hours_div.text.split('\n')[1:]:
        hours += h.replace(' ', '') + ' '

    main = driver.find_element_by_css_selector('div#vtsikinlineContent-gridContainer')
    divs = main.find_elements_by_css_selector('div.txtNew')

    all_store_data = []
    switch = True
    for div in divs:
        if switch:
            location_name = div.text
            switch = False

        else:
            content = div.text.split('\n')

            if len(content) == 3:
                street_address = content[0]
                city, state, zip_code = addy_ext(content[1])
                phone_number = content[2]
            else:
                street_address = content[1]
                city, state, zip_code = addy_ext(content[2])
                phone_number = content[3]

            lat = '<MISSING>'
            longit = '<MISSING>'
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)
            switch = True

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
