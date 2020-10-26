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

def parse_address(addy_string):
    parsed_add = usaddress.tag(addy_string)[0]

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

    street_address = street_address.strip()
    if street_address == '':
        street_address = '<MISSING>'

    city = parsed_add['PlaceName']
    state = parsed_add['StateName']
    zip_code = parsed_add['ZipCode']

    return street_address, city, state, zip_code

def fetch_data():
    locator_domain = 'https://www.tiffany.com/'
    ext = 'jewelry-stores/store-list/united-states/'
    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_css_selector('div.store-list__store-item')
    link_list = []
    print(len(locs))
    for loc in locs:
        store_link = loc.find_element_by_css_selector('a.cta')
        link_list.append(store_link.get_attribute('href'))

    all_store_data = []
    for i, link in enumerate(link_list):
        driver.get(link)
        driver.implicitly_wait(10)
        print(link)
        print(i)
        location_name = driver.find_element_by_css_selector('h1.heading').text
        print(location_name)

        addy = driver.find_element_by_css_selector('div.store-address').text.replace('\n', ' ')
        if 'Westfield Century City' in addy:
            street_address = 'Westfield Century City'
            city = 'Los Angeles'
            state = 'CA'
            zip_code = '90067'
        elif 'Santa Monica Place' in addy:
            street_address = 'Santa Monica Place'
            city = 'Santa Monica'
            state = 'CA'
            zip_code = '90401'

        else:
            street_address, city, state, zip_code = parse_address(addy)

        print(street_address, city, state, zip_code)

        hours = driver.find_element_by_css_selector('p.store-timings').text.replace('\n', ' ').strip()
        print(hours)
        phone_number = driver.find_element_by_css_selector('p.store-contact').find_element_by_css_selector(
            'a.tel-link').get_attribute('data-interaction-name').strip()
        print(phone_number)

        lat = driver.find_element_by_css_selector('tiffany-maps').get_attribute('markeratlat')
        longit = driver.find_element_by_css_selector('tiffany-maps').get_attribute('markeratlng')
        print(lat, longit)

        store_number = '<MISSING>'
        location_type = '<MISSING>'

        country_code = 'US'

        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
