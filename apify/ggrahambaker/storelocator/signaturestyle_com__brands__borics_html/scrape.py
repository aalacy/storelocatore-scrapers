import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
from sgzip import ClosestNSearch
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

    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    locator_domain = 'https://www.signaturestyle.com/brands/borics.html'

    search = ClosestNSearch()
    search.initialize(country_codes = ['us', 'ca'])

    MAX_DISTANCE = 25

    coord = search.next_coord()
    all_store_data = []
    dup_tracker = []
    while coord:    
        x = coord[0]
        y = coord[1]

        url = 'https://info3.regiscorp.com/salonservices/siteid/100/salons/searchGeo/map/' + str(x) + '/' + str(y) + '/0.5/0.5/true'

        r = session.get(url, headers=HEADERS)
        
        res_json = json.loads(r.content)['stores']

        result_coords = []
        result_coords.append((x, y))
        
        for loc in res_json:
            lat = loc['latitude']
            longit = loc['longitude']
            result_coords.append((lat, longit))
            
            if loc['actualSiteId'] != 13:
                continue
            
            store_number = loc['storeID']
            
            if store_number not in dup_tracker:
                dup_tracker.append(store_number)
            else:
                continue
                
            page_json_url = 'https://info3.regiscorp.com/salonservices/siteid/100/salon/' + str(store_number)
            
            r = session.get(page_json_url, headers=HEADERS)
        
            loc = json.loads(r.content)
            
            location_name = loc['name']
            street_address = loc['address']
            city = loc['city']
            state = loc['state']
            zip_code = loc['zip']
            if len(zip_code.split(' ')) == 2:
                country_code = 'CA'
            else:
                country_code = 'US'
                
            phone_number = loc['phonenumber']
                
            
            hours_obj = loc['store_hours']
            hours = ''
            for part in hours_obj:
                day = part['days']
                hour_range = part['hours']['open'] + ' - ' + part['hours']['close']
                
                hours += day + ' ' + hour_range + ' '            
            

            if hours == '':
                hours = '<MISSING>'
            location_type = '<MISSING>'
            page_url = '<MISSING>'
            
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                        store_number, phone_number, location_type, lat, longit, hours, page_url]

            
            all_store_data.append(store_data)
            
        search.max_count_update(result_coords)    
        coord = search.next_coord()  


    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
