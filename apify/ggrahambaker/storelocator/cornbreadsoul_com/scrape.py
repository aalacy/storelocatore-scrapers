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
    if 'StreetName' in parsed_add:
        street_address += parsed_add['StreetName'] + ' '
    if 'StreetNamePostType' in parsed_add:
        street_address += parsed_add['StreetNamePostType'] + ' '
    if 'OccupancyType' in parsed_add:
        street_address += parsed_add['OccupancyType'] + ' '
    if 'OccupancyIdentifier' in parsed_add:
        street_address += parsed_add['OccupancyIdentifier'] + ' '
    city = parsed_add['PlaceName']
    state = parsed_add['StateName']
    zip_code = parsed_add['ZipCode']

    return street_address, city, state, zip_code

def fetch_data():
    locator_domain = 'https://cornbreadsoul.com/'
    ext = 'cornbread_soul_locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    loc_list = driver.find_element_by_css_selector('ul#menu-locations').find_elements_by_css_selector('a')

    link_list = []
    for loc in loc_list:
        link_list.append(loc.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        
        location_name = driver.find_element_by_css_selector('div.page-title-wrapper').text

        addy = driver.find_element_by_css_selector('i.fa.fa-map-marker').find_element_by_xpath('../../../..').find_element_by_css_selector('p').text.replace('\n', ' ')

        street_address, city, state, zip_code = parse_address(addy)
        
        phone_number = driver.find_element_by_css_selector('i.fa.fa-phone-square').find_element_by_xpath('../../../..').text
                
        hours = driver.find_element_by_css_selector('i.fa.fa-clock-o').find_element_by_xpath('../../../..').text
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        lat = '<MISSING>'
        longit = '<MISSING>'
        page_url = link
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
