import csv
from bs4 import BeautifulSoup
import re
import json
import sgzip
import http.client as http_client
import ssl
import gzip
import certifi
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('gamestop_com')
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
        addresses = []
        search = sgzip.ClosestNSearch()
        search.initialize()
        MAX_RESULTS = 10000
        MAX_DISTANCE = 100
        current_results_len = 0  # need to update with no of count.
        coord = search.next_coord()
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
            'Host': 'www.gamestop.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive'
        }

        while coord:
            result_coords = []
            lat = coord[0]
            lng = coord[1]
            context = ssl.SSLContext(ssl.PROTOCOL_TLS)
            context.load_default_certs(purpose=ssl.Purpose.SERVER_AUTH)
            certs_path = certifi.where()
            context.load_verify_locations(cafile=certs_path)
            context.verify_mode = ssl.CERT_REQUIRED
            context.check_hostname = True
            conn = http_client.HTTPSConnection("www.gamestop.com", context=context)
            conn.connect()
            conn.request("GET",'/on/demandware.store/Sites-gamestop-us-Site/default/Stores-FindStores?radius='+str(MAX_DISTANCE)+"&lat="+str(lat)+"&long="+str(lng), headers=HEADERS)
            res = conn.getresponse()
            data = gzip.decompress(res.read())
            json_data = json.loads(data)
            if "stores" in json_data:
                current_results_len = len(json_data['stores'])
                for i in json_data['stores']:
                    store_number = i['ID']
                    location_name = i['name']
                    street_address = str(i['address1'])+" "+str(i['address2'])
                    city = i['city']
                    state = i['stateCode']
                    zipp = i['postalCode']
                    country_code = i['countryCode']
                    phone = i['phone']
                    latitude = i['latitude']
                    longitude = i['longitude']
                    location_type = "GameStop"
                    hours_of_operation = i['storeHours']
                    name = location_name.replace('-','')
                    page_url = "https://www.gamestop.com/store/us/"+str(state.lower())+"/"+str(city.lower().replace(' ','-'))+"/"+str(store_number)+"/"+str(name.replace(' ','-').replace("--",'-').replace('.','').lower())
                    store = []
                    result_coords.append((latitude, longitude))
                    store.append("http://www.gamestop.com")
                    store.append(location_name if location_name else '<MISSING>')
                    store.append(street_address.replace(" None","") if street_address else '<MISSING>')
                    store.append(city if city else '<MISSING>')
                    store.append(state if state else '<MISSING>')
                    store.append(zipp if zipp else '<MISSING>')
                    store.append(country_code if country_code else '<MISSING>')
                    store.append(store_number if store_number else '<MISSING>')
                    store.append(phone if phone else '<MISSING>')
                    store.append(location_type if location_type else '<MISSING>')
                    store.append(latitude if latitude else '<MISSING>')
                    store.append(longitude if longitude else '<MISSING>')
                    store.append(hours_of_operation if hours_of_operation else '<MISSING>')
                    store.append(page_url)
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    yield store
            if current_results_len < MAX_RESULTS:
                search.max_distance_update(MAX_DISTANCE)
            elif current_results_len == MAX_RESULTS:
                search.max_count_update(result_coords)
            else:
                raise Exception("expected at most " + str(MAX_RESULTS) + " results")
            coord = search.next_coord()
          
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
