import csv
import os
from sgselenium import SgSelenium
import time
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_addy(addy):
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

def fetch_data():
    locator_domain = 'https://pls247.com/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain)

    state_list = driver.find_element_by_id('state_list').find_elements_by_css_selector('option')

    abbr_list = []
    for state in state_list:
        abbr = state.get_attribute('value').strip()
        if abbr == '':
            continue
        
        abbr_list.append(abbr.lower())

    link_list = []
    for abbr in abbr_list:
        link = 'https://pls247.com/' + abbr + '/store-locator.html'
        driver.get(link)
        driver.implicitly_wait(15)
        
        page_inc = 0
        print(link)
        while True:
            page_inc += 1
            all_locs_collected = False
            driver.get(link + '#page=' + str(page_inc))
            time.sleep(3)
            driver.implicitly_wait(15)

            locs = driver.find_elements_by_css_selector('div.row')
            for loc in locs:
                loc_link = loc.find_element_by_css_selector('a').get_attribute('href')
                if loc_link in link_list:
                    all_locs_collected = True
                else:
                    link_list.append(loc_link)
                
            if all_locs_collected:
                break

    all_store_data = []
    dup_tracker = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        
        lat = driver.find_element_by_xpath('//meta[@itemprop="latitude"]').get_attribute('content')
        longit = driver.find_element_by_xpath('//meta[@itemprop="longitude"]').get_attribute('content')
        
        phone_number = driver.find_element_by_xpath('//span[@itemprop="telephone"]').text
        if phone_number in dup_tracker:
            continue
        else:
            dup_tracker.append(phone_number)
            
        hours = ''
        
        hour_metas = driver.find_elements_by_xpath('//meta[@itemprop="openingHours"]')
        for day in hour_metas:
            hours += day.get_attribute('content') + ' '
            if 'Sun' in hours:
                break

        hours = hours.strip()
        if hours == '':
            hours = 'Open 24/7'
            
        addy = driver.find_element_by_xpath('//h1[@itemprop="address"]').text
        street_address, city, state, zip_code = parse_addy(addy)
        
        country_code = 'US'
        page_url = link
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        location_name = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
        
        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
