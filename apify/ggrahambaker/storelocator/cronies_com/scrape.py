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

def fetch_data():
    locator_domain = 'http://cronies.com/'
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    divs = driver.find_elements_by_css_selector('div.six.columns')
    switch = True
    all_store_data = []
    for div in divs:
        if switch:
            # content
            phone_number = div.find_element_by_css_selector('div.locationPhone').text.replace('Phone:', '').strip()

            hours = div.find_element_by_css_selector('ul.opening-hours-list').text.replace('\n', ' ')

            location_name = div.find_element_by_css_selector('span.locationName').text

            city_state = location_name.strip().split(' ')

            if len(city_state) == 2:
                city = city_state[0]
                state = city_state[1]
            elif len(city_state) == 3:
                city = city_state[0] + ' ' + city_state[1]
                state = city_state[2]
            zip_code = '<MISSING>'
            street_address = div.find_element_by_css_selector('div.locationAddress').text

            switch = False

        else:
            # map and push to array
            href = div.find_element_by_css_selector('div.mapLink').find_element_by_css_selector('a').get_attribute(
                'href')

            start_idx = href.find('/@')
            if start_idx > 0:
                end_idx = href.find('z/data')
                coords = href[start_idx + 2: end_idx].split(',')
                lat = coords[0]
                longit = coords[1]
            else:
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
