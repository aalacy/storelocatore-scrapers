import csv
import os
from sgselenium import SgSelenium
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.iloveubq.com/'
    ext = '#locations'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('div#collapseMaryland')
    locs = main.find_elements_by_css_selector('div.location-store')
    link_list = []
    for loc in locs:
        link_list.append(loc.find_element_by_css_selector('a.link').get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        location_name = driver.find_element_by_css_selector('span.title').text

        addy = driver.find_element_by_css_selector('div.address').text

        parsed_add = usaddress.tag(addy)[0]
        if 'AIRPORT' in addy:
            street_address = 'BALTIMORE/WASHINGTON INTERNATIONAL THURGOOD MARSHALL AIRPORT (BWI)'
            city = 'BALTIMORE'
            state = 'MD'
            zip_code = '<MISSING>'
            phone_number = '<MISSING>'
        else:
            street_address = ''

            if 'AddressNumber' in parsed_add:
                street_address += parsed_add['AddressNumber'] + ' '
            if 'StreetNamePreDirectional' in parsed_add:
                street_address += parsed_add['StreetNamePreDirectional'] + ' '
            if 'StreetName' in parsed_add:
                street_address += parsed_add['StreetName'] + ' '
            if 'StreetNamePostType' in parsed_add:
                street_address += parsed_add['StreetNamePostType'] + ' '
            if 'OccupancyType' in parsed_add:
                street_address += parsed_add['OccupancyType'] + ' '
            if 'OccupancyIdentifier' in parsed_add:
                street_address += parsed_add['OccupancyIdentifier'] + ' '

            if 'PlaceName' in parsed_add:
                city = parsed_add['PlaceName']
            else:
                city = '<MISSING>'

            if 'StateName' in parsed_add:
                state = parsed_add['StateName']
            else:
                state = '<MISSING>'

            if 'ZipCode' in parsed_add:
                zip_code = parsed_add['ZipCode']
            else:
                zip_code = '<MISSING>'

            phone_number = driver.find_element_by_css_selector('div.phone').text

        details = driver.find_element_by_css_selector('div.store-details')
        hours = details.text.replace('Store Hours', '').replace('\n', ' ').strip()

        lat = '<MISSING>'
        longit = '<MISSING>'

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
