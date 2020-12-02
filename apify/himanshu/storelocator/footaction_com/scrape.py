import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import time
from sglogging import SgLogSetup
import sgzip
from sgzip import DynamicGeoSearch, SearchableCountries
logger = SgLogSetup().get_logger('footaction')

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    search = DynamicGeoSearch(country_codes=[SearchableCountries.USA,], max_radius_miles=100, max_search_results=100)
    search.initialize()
    coord = search.next()

    addressess = []
    base_url = "https://www.footaction.com"

    headers = {
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://www.gulfoil.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest'
    }

    while coord:
        result_coords =[]
        
        headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
        }
        locator_domain = "https://www.footaction.com"
        data =session.get('https://www.footaction.com/api/stores?latitude='+str(coord[0])+'&longitude='+str(coord[1])+'&timestamp=1606730041839', headers=headers).json()
        if 'stores' in data:
            for td in data['stores']:
                street_address = td['address']['line1'].lower()
                phone = td['address']['phone']
                zipp = td['address']['postalCode']
                city = td['address']['town'].lower()
                location_name = td['displayName']
                state = td['address']['region']['isocodeShort']
                country_code = td['address']['country']['isocode']
                storeNumber = td['storeNumber']
                latitude = td['geoPoint']['latitude']
                longitude = td['geoPoint']['longitude']        
                result_coords.append((latitude,longitude))
                store = []
                store.append('https://www.footaction.com/')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code)
                store.append('<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append('<MISSING>')
                store.append(latitude)
                store.append(longitude)
                store.append('<MISSING>')
                store.append('<MISSING>')
                if str(store[2]) in addressess:
                    continue
                addressess.append(str(store[2]))
                store = [str(x).strip() if x else "<MISSING>" for x in store]
                yield store
        search.update_with(result_coords)
        coord = search.next()
    
def scrape():
    data = fetch_data()

    write_output(data)

scrape()
