import csv
import os
from sgselenium import SgSelenium
import json
import usaddress
import re


def addy_parser(addy):
    parsed_add = usaddress.tag(addy)[0]

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

    street_address = street_address.strip()
    city = parsed_add['PlaceName'].strip()
    state = parsed_add['StateName'].strip()
    zip_code = parsed_add['ZipCode'].strip()
    
    return street_address, city, state, zip_code





def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.adventurelanding.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)


    link_list = []
    states = driver.find_elements_by_css_selector('div.fusion-builder-row.fusion-builder-row-inner.fusion-row' )
    for state in states:
        locs = state.find_elements_by_css_selector('div.fusion-layout-column')
        for loc in locs:
            link = loc.find_elements_by_css_selector('a')
            if len(link) > 0:
                link_list.append(link[0].get_attribute('href'))



    all_store_data = []
    for link in link_list:
        
        hours_link = 'plan-your-visit/hours/'
        addy_link = 'plan-your-visit/directions/'

        start = link.find('//')
        end = link.find('.adventure')
        location_name = link[start + 2:end].replace('-', ' ')

        driver.get(link + addy_link)
        driver.implicitly_wait(10)
        js_blocks = driver.find_elements_by_xpath('//script[@type="text/javascript"]')
        for bloc in js_blocks:
            bloc_text = bloc.get_attribute('innerHTML')
            if 'addresses:' in bloc_text:
                for line in bloc_text.splitlines():
                    if line.strip().startswith('addresses:'):
                        start = line.strip().find('{')
                        end = line.strip().find('}')
                        addy_json = json.loads(line.strip()[start:end + 1])
                        
                        street_address, city, state, zip_code = addy_parser(addy_json['address'])
                        lat = addy_json['latitude']
                        longit = addy_json['longitude']
                        
        ps = driver.find_elements_by_css_selector('p')
        for p in ps:
            num = re.search(r'1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]{2})\W*([0-9]{4})(\se?x?t?(\d*))?', p.text)
            if num:
                phone_number = num.group().strip()
                break

        
        
        # hours_link
        driver.get(link + hours_link)
        driver.implicitly_wait(10)
        
        hours = driver.find_element_by_css_selector('div.fusion-text').text.replace('\n', ' ')
        
        
        country_code = 'US'

        location_type = '<MISSING>'
        page_url = link
        store_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        all_store_data.append(store_data)

        

        
        
        


    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
