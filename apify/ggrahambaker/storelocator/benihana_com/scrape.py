import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import usaddress
import json

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
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.benihana.com/' 
    ext = 'wp-content/themes/grandrestaurant-child-new/js/locations.json'
    r = session.get(locator_domain + ext, headers = HEADERS)
    locs = json.loads(r.content)

    all_store_data = []
    for loc in locs:
        if loc['comingSoon']:
            continue
            
        if 'United' not in loc['country']:
            continue
     
        location_name = BeautifulSoup(loc['name'], 'html.parser').text.strip()
        if 'EVENTS' in location_name:
            location_type = 'Events Only'
        elif 'CLOSED' in location_name:
            continue
        else:
            location_type = 'Resturant'
            
        lat = loc['lat']
        longit = loc['lng']
        
        if 'http' in loc['URL']:
            page_url = loc['URL']
        else:
            page_url = locator_domain[:-1] + loc['URL']
            
        addy = BeautifulSoup(loc['Address'], 'html.parser').text.strip()
        if 'Delivery' in addy:
            continue
            
        street_address, city, state, zip_code = parse_address(addy)
        phone_number = BeautifulSoup(loc['Phone'], 'html.parser').text.strip()
        if phone_number == '':
            phone_number = '<MISSING>'

        hours = "Su-Th 11:30-22:30 Fr-Sa 11:30-22:30"
        
        country_code = 'US'
        store_number = '<MISSING>'
        
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        
    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
