import csv
import os
from sgselenium import SgSelenium
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
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
    if 'StreetNamePreType' in parsed_add:
        street_address += parsed_add['StreetNamePreType'] + ' '
    if 'StreetName' in parsed_add:
        street_address += parsed_add['StreetName'] + ' '
    if 'StreetNamePostType' in parsed_add:
        street_address += parsed_add['StreetNamePostType'] + ' '
    if 'OccupancyType' in parsed_add:
        street_address += parsed_add['OccupancyType'] + ' '
    if 'OccupancyIdentifier' in parsed_add:
        street_address += parsed_add['OccupancyIdentifier'] + ' '
        
    if 'PlaceName' not in parsed_add:
        city = '<MISSING>'
    else:
        city = parsed_add['PlaceName']
    
    if 'StateName' not in parsed_add:
        state = '<MISSING>'
    else:
        state = parsed_add['StateName']
        
    if 'ZipCode' not in parsed_add:
        zip_code = '<MISSING>'
    else:
        zip_code = parsed_add['ZipCode']

    return street_address, city, state, zip_code

def fetch_data():
    locator_domain = 'https://jacksonhealth.org/' 
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    locs = driver.find_elements_by_css_selector('div.location-single-loop-instance')

    all_store_data = []
    for loc in locs:
        location = loc.find_element_by_css_selector('h2')
        page_url = location.find_elements_by_css_selector('a')
        if len(page_url) == 1:
            page_url = page_url[0].get_attribute('href')#.text
        else:
            page_url = '<MISSING>'
        location_name = location.text
   
        if 'CLOSED' in location_name:
            continue
        
        location_type = loc.find_element_by_css_selector('p').text
        
        links = loc.find_elements_by_css_selector('a')

        for l in links:
            if '/directions/' in l.get_attribute('href'):
                if '#' not in l.get_attribute('href'):
                    page_url = l.get_attribute('href')
            if 'place/' in l.get_attribute('href'): 
                addy = l.get_attribute('href').split('place/')[1].replace('%20', ' ').replace('+', ' ')
                if 'Jackson Memorial Hospital 1611 NW 12 Ave Ambulatory Care Center' in addy:
                    street_address = '1611 NW 12 Ave'
                    city = 'Miami'
                    state = 'FL'
                    zip_code = '33136'
                else:
                    addy = addy.replace('Second Floor', '')
                    street_address, city, state, zip_code = parse_address(addy)
                    street_address = street_address.split('Suite')[0].strip().split('Room')[0].strip().split('Unit')[0].strip().replace(',', '').strip()

            if 'tel:' in l.get_attribute('href'):
                phone_number = l.get_attribute('href').replace('tel:', '')
        
        country_code = 'US'
        store_number = '<MISSING>'
        hours = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
