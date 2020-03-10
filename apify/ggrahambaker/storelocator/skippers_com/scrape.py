import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import usaddress


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
    url = 'https://skippers.com/wp-json/wpgmza/v1/markers/base64eJyrVkrLzClJLVKyUqqOUcpNLIjPTIlRsopRMoxR0gEJFGeUgsSKgYLRsbVKtQCV7hBN'

    HEADERS = {'Host': 'skippers.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'X-WP-Nonce': '59aa4fe148',
    'X-Requested-With': 'XMLHttpRequest',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'https://skippers.com/locations/',
    'Cookie': 'tk_ai=woo%3A0kJozCAwfRaGyVyFKY3%2Bv1q%2F',
    'Pragma': 'no-cache',
    'Cache-Control': 'no-cache'}


    session = SgRequests()

    r = session.get(url, headers = HEADERS)

    loc_info = json.loads(r.content)
    locator_domain = 'https://skippers.com/'
    all_store_data = []
    for loc in loc_info:
        location_name = loc['title']
        store_number = loc['id']
        street_address, city, state, zip_code = parse_address(loc['address'])
        
        
        loc['description']
        
        phone_number = loc['description'].strip()
        if phone_number == '':
            phone_number = '<MISSING>'
        else:
            soup = BeautifulSoup(phone_number, 'html.parser')
            phone_number = soup.find('p').text.strip()
        
        lat = loc['lat']
        longit = loc['lng']
        country_code = 'US'
        
        location_type = '<MISSING>'
        hours = '<MISSING>'
        page_url = '<MISSING>'
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]


        all_store_data.append(store_data)







    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
