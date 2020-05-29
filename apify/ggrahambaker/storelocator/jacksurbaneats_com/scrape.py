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
    locator_domain = 'http://www.jacksurbaneats.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_css_selector('div.et_pb_text_inner')
    all_store_data = []
    for loc in locs:
        cont = loc.text.split('\n')
        if len(cont) > 1:
            location_name = cont[0]
            street_address = cont[2]
            city, state, zip_code = addy_ext(cont[3])
            phone_number = cont[4]
            if phone_number == '.':
                phone_number = '<MISSING>'

            hours = ''
            for h in cont[6:]:
                hours += h + ' '

            hours = hours.strip()
            link = loc.find_element_by_css_selector('a').get_attribute('href')

            coords = link[link.find('/@') + 2:link.find('z/d')].split(',')

            if 'google' in coords[0]:
                lat = '<MISSING>'
                longit = '<MISSING>'
            else:
                lat = coords[0]
                longit = coords[1]


            country_code = 'US'
            location_type = '<MISSING>'
            store_number = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
