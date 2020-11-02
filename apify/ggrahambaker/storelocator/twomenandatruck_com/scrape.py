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
    locator_domain = 'https://twomenandatruck.com/'
    driver = SgSelenium().chrome()

    all_store_data = []
    all_states = get_states()

    for state in all_states:
        link = 'https://twomenandatruck.com/movers/' + state
        driver.get(link)
        driver.implicitly_wait(10)

        if 'The website encountered an unexpected error.' in driver.find_element_by_css_selector('body').text:
            continue

        res = driver.find_element_by_css_selector('div#location-results')
        locs = res.find_elements_by_css_selector('div.result')
        for loc in locs:
            street_address = loc.find_element_by_css_selector('span.address-line1').text
            if 'location only' in street_address.lower():
                continue

            city = loc.find_element_by_css_selector('span.locality').text
            state = loc.find_element_by_css_selector('span.administrative-area').text
            zip_code = loc.find_element_by_css_selector('span.postal-code').text

            phone_number = loc.find_element_by_css_selector('a.phone.contact.contact--phone').get_attribute(
                'data-display')

            geo_href = loc.find_element_by_css_selector('a.contact.contact--directions').get_attribute('href')

            start_idx = geo_href.find('place/')
            coords = geo_href[start_idx + 6:].split(',%20')

            lat = coords[0]
            longit = coords[1]

            country_code = 'US'
            store_number = '<MISSING>'
            hours = '<MISSING>'
            location_type = '<MISSING>'
            location_name = '<MISSING>'

            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                          store_number, phone_number, location_type, lat, longit, hours]
            all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def get_states():
    states = ['AK',
              'AL',
              'AR',
              'AZ',
              'CA',
              'CO',
              'CT',
              'DC',
              'DE',
              'FL',
              'GA',
              'HI',
              'IA',
              'ID',
              'IL',
              'IN',
              'KS',
              'KY',
              'LA',
              'MA',
              'MD',
              'ME',
              'MI',
              'MN',
              'MO',
              'MS',
              'MT',
              'NA',
              'NC',
              'ND',
              'NE',
              'NH',
              'NJ',
              'NM',
              'NV',
              'NY',
              'OH',
              'OK',
              'OR',
              'PA',
              'PR',
              'RI',
              'SC',
              'SD',
              'TN',
              'TX',
              'UT',
              'VA',
              'VT',
              'WA',
              'WI',
              'WV',
              'WY']
    all_states = []
    for state in states:
        all_states.append(state.lower())

    return all_states

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
