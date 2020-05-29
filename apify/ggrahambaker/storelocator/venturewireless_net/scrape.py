import csv
import os
from sgselenium import SgSelenium

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def addy_ext(addy):
    addy = addy.split(',')
    city = addy[0]
    state_zip = ' '.join(addy[1].split()).split(' ')
    state = state_zip[0].strip()
    zip_code = state_zip[1].strip()
    return city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.venturewireless.net/' 

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    conts = driver.find_elements_by_css_selector('div.txtNew')
    all_store_data = []
    for cont in conts:
        info = cont.text.split('\n')
        if len(info) < 2:
            continue

        location_name = info[0]
        street_address = info[1].strip()
        city, state, zip_code = addy_ext(info[2])
        phone_number = info[3]

        hours = ''
        for h in info[5:]:
            hours += h + ' '
            
        hours = hours.strip()
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
