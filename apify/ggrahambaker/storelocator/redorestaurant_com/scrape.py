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
    locator_domain = 'https://www.redorestaurant.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_css_selector('div.six.columns')
    all_store_data = []
    for loc in locs:
        cont = loc.text.split('\n')
        if len(cont) > 30:
            continue
        elif len(cont) < 10:
            continue

        cont = loc.text.split('\n')

        href = loc.find_element_by_css_selector('a').get_attribute('href')

        start_idx = href.find('/@')
        end_idx = href.find('z/d')

        coords = href[start_idx + 2: end_idx].split(',')

        lat = coords[0]
        longit = coords[1]

        if len(cont) == 22:
            street_address = cont[2]
            city, state, zip_code = addy_ext(cont[3])
            phone_number = cont[4].replace('Tel:', '').strip()
            hours = ''
            for h in cont[8:-3]:
                hours += h + ' '

        else:
            if len(cont) == 19:
                off = 2
            else:
                off = 0

            street_address = cont[1]
            city, state, zip_code = addy_ext(cont[2])
            phone_number = cont[3].replace('Tel:', '').strip()

            hours = ''

            for h in cont[off + 6:-3]:
                hours += h + ' '

        location_name = city
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
