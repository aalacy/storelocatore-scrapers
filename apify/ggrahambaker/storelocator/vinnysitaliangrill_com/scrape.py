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
    locator_domain = 'http://www.vinnysitaliangrill.com/'
    ext = 'locations/'
    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_css_selector('div.div_location')

    seen_count = 0
    all_store_data = []
    for loc in locs:
        address = loc.find_element_by_css_selector('p.descrizione_location').text.split('\n')
        print(address)
        street_address = address[0]
        if 'Garrisonville' in street_address:
            seen_count += 1
            print(seen_count)
            if seen_count == 2:
                continue

        if len(address) == 3:
            city, state, zip_code = addy_ext(address[2])
        elif '241 Connor Drive, unit L' in street_address:
            city = '<MISSING>'
            state = '<MISSING>'
            zip_code = '<MISSING>'
        elif '20 Plantation Drive' in street_address:
            city = 'Fredericksburg'
            state = 'VA'
            zip_code = '22406'
        elif 'Richmond Tappahannock Hwy' in street_address:
            city = 'Aylett'
            state = 'VA'
            zip_code = '<MISSING>'
        else:
            city, state, zip_code = addy_ext(address[1])

        phone_number = loc.find_element_by_css_selector('p.telefono_location').text.replace('Phone:', '').strip()
        print(phone_number)

        country_code = 'US'
        location_name = '<MISSING>'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        hours = '<MISSING>'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
