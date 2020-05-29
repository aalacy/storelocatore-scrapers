import csv
import os
from sgselenium import SgSelenium
import usaddress
from sgrequests import SgRequests
from bs4 import BeautifulSoup

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
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'http://omnifamilyhealth.org/' 
    ext = 'locations/'

    driver = SgSelenium().chrome()
    driver.get(locator_domain + ext)

    titles = driver.find_elements_by_css_selector('div.location_title')
    dirs = driver.find_elements_by_css_selector('a#directions')
    infos = driver.find_elements_by_css_selector('div.location_info')

    all_store_data = []
    for i, title in enumerate(titles):
        location_name = title.text

        page_url = dirs[i].get_attribute('href') 
        dirty_info = infos[i].text.strip().split('\n')
        info = [i for i in dirty_info if i != '']

        if len(info) == 2:
            street_address, city, state, zip_code = parse_address(info[0])
            hours = info[1]
        elif len(info) == 3:
            street_address, city, state, zip_code = parse_address(info[0] + ' ' + info[1])
            hours = info[2]
        elif len(info) == 4:
            street_address, city, state, zip_code = parse_address(info[0] + ' ' + info[2])
            hours = info[3]
            
        else:
            if 'Hours' in info[1]:
                street_address, city, state, zip_code = parse_address(info[0])
                hours = ''
                for h in info[2:]:
                    hours += h + ' '
            elif 'Hours' in info[2]:
                street_address, city, state, zip_code = parse_address(info[0] + ' ' + info[1])
                hours = ''
                for h in info[3:]:
                    hours += h + ' '
                    
            else:
                street_address, city, state, zip_code = parse_address(info[0] + ' ' + info[2])
                hours = ''
                for h in info[4:]:
                    hours += h + ' '

        country_code = 'US'
        store_number = page_url.split('=')[1]
        phone_number = '<MISSING>'
        location_type = '<MISSING>'

        r = session.get(page_url, headers = HEADERS)
        soup = BeautifulSoup(r.content, 'html.parser')
        
        anchor = soup.find('div', {'class': 'google-maps'})#.find('iframe')
        google = anchor.find('iframe')['src']
        start = google.find('!2d')
        end = google.find('!2m')
        coords = google[start + 3: end].split('!3d')
        longit = coords[0]
        lat = coords[1].split('!3m')[0]
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)

    driver.quit()
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
