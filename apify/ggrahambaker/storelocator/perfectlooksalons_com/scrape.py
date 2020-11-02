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
    locator_domain = 'https://www.perfectlooksalons.com/'
    ext = 'family-haircare/'
    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    main = driver.find_element_by_css_selector('ul.side-locations')
    links = main.find_elements_by_css_selector('a')
    state_list = []
    for link in links:
        state_list.append(link.get_attribute('href'))
        
    link_list = []
    for state in state_list:
        driver.get(state)
        driver.implicitly_wait(10)
        
        locs = driver.find_elements_by_css_selector('div.location-content')
        for loc in locs:
            link = loc.find_element_by_css_selector('a').get_attribute('href')
            link_list.append(link)
        
    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        
        location_name = driver.find_element_by_css_selector('h1.uk-article-title').text
    
        hours = driver.find_element_by_css_selector('p.hours').text.replace('Store Hours:', '').replace('\n', ' ')
        cont = driver.find_element_by_css_selector('div.uk-width-large-2-5').text.split('\n')

        street_address, city, state, zip_code = parse_address(cont[0] + ' ' + cont[1])
        phone_number = cont[2]

        href = driver.find_element_by_xpath('//a[contains(@href,"maps.google.com/maps")]').get_attribute('href')
        start = href.find('?ll=')
        coords = href[start + 4:].split(',')
        lat = coords[0]
        longit = coords[1].split('&')[0]
        
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        country_code = 'US'
        locator_domain = 'https://www.perfectlooksalons.com/'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, link]

        all_store_data.append(store_data)
        
    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
