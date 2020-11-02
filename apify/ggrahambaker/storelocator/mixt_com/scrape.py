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
    locator_domain = 'https://www.mixt.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    stores = driver.find_elements_by_css_selector('div.grand-text')

    all_store_data = []
    for store in stores:
        content = store.text.split('\n')
        
        if 'OPENING SOON' in content[0]:
            continue
        if len(content) > 3:
            if 'CITY CENTER BISHOP RANCH' in content[0]:
                street_address = content[1]
                city, state, zip_code = addy_ext(content[2])
            else:
                if 'Los Angeles' in content[2]:
                    street_address = content[1]
                else:
                    street_address = content[0]
                city, state, zip_code = addy_ext(content[2])

            hours = ''
            for h in content[3:-2]:
                hours += h + ' '

            href = store.find_element_by_css_selector('a').get_attribute('href')

            start_idx = href.find('/@')
            end_idx = href.find('z/data')
            if start_idx > 0:
                coords = href[start_idx + 2:end_idx].split(',')
                lat = coords[0]
                longit = coords[1]
            else:
                lat = '<MISSING>'
                longit = '<MISSING>'

            location_name = '<MISSING>'
            country_code = 'US'
            store_number = '<MISSING>'
            location_type = '<MISSING>'
            phone_number = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
