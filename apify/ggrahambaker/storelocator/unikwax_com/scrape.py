import csv
import os
from sgselenium import SgSelenium
from bs4 import BeautifulSoup
import usaddress

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

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://unikwax.com/' 
    ext = 'studio-locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    states = driver.find_elements_by_css_selector('div.a')

    link_list = []
    for state in states:
        locs = state.find_elements_by_css_selector('li')
        for loc in locs:
            soup = BeautifulSoup(loc.get_attribute('innerHTML'), 'html.parser')
            page_url = soup.find('a', {'class': 'location__postlink'})['href']
            
            location_name = soup.find('span', {'class': 'location__title'}).text.strip()
            street_address = soup.find('span', {'class': 'location__address'}).text.strip()
            if 'closed' in street_address:
                continue
            link_list.append(page_url)
 
    all_store_data = []
    for link in link_list:
        driver.get(link)
        driver.implicitly_wait(10)
        
        location_name = driver.find_element_by_css_selector('h1').text.strip()
        
        cols = driver.find_element_by_css_selector('div.info').find_elements_by_css_selector('div.col-sm-6')
        
        phone_number = cols[0].find_element_by_css_selector('a.number').text
    
        addy = cols[0].find_element_by_css_selector('a.direction').get_attribute('href').replace('https://maps.google.com/?daddr=%20Uni%20K%20Wax%20Studio', '').replace('%20', ' ').strip()
        if '22-22 Jackson Avenue' in addy:
            street_address = '22-22 Jackson Avenue' 
            city = 'Long Island City'
            state = '<MISSING>'
            zip_code = '11101'
        elif '665 Lexington Ave Manhattan' in addy:
            street_address = '665 Lexington Ave'
            city = 'New York' 
            state = 'New York'
            zip_code = '10022'
        elif '606 Washington Street' in addy:
            street_address = '606 Washington Street'
            city = 'Hoboken' 
            state = 'New Jersey'
            zip_code =  '07030'
        else:
            street_address, city, state, zip_code = parse_address(addy)

        hours = cols[1].text.replace('\n', ' ').replace('Studio Hours', '').strip()

        obj = driver.execute_script('return gmwMapObjects')['unik']['locations'][0]
        lat = obj['lat']
        longit = obj['lng']
        
        country_code = 'US'
        store_number = '<MISSING>'
        
        location_type = '<MISSING>'
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
