import csv
import os
from sgselenium import SgSelenium
import json
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
    locator_domain = 'https://www.coyoteuglysaloon.com/'
    ext = 'map/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    groups = driver.find_element_by_css_selector('section#newsarchive').find_elements_by_css_selector('dl')

    link_list = []
    for group in groups[7:]:
        links = group.find_elements_by_css_selector('a')
        for link in links:
            link_list.append(link.get_attribute('href'))

    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        info = driver.find_element_by_css_selector('div#detailinfo').text.split('\n')

        if 'daytona' in info[1]:
            phone_number = '(386) 256-4954'
        else:
            phone_number = info[1].replace('PHONE', '').strip().split(' ')[0]
            if 'UGLY' in phone_number:
                phone_number = phone_number.replace('UGLY', '8459')
        hours = ''
        for h in info:
            if 'pm-' in h or 'am-' in h:
                hours += h + ' '

        address = driver.find_element_by_css_selector('div#mapinfo').text.split('\n')
        location_name = address[1]
        addy = address[-7]

        parsed_add = usaddress.tag(addy)[0]

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

        data = driver.find_element_by_css_selector('div.wpgmza_map').get_attribute('data-settings')
        json_geo = json.loads(data)
        # print(json_geo['map_start_location'].split(','))
        coords = json_geo['map_start_location'].split(',')
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
