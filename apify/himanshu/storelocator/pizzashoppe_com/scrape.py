import csv
import requests
import json
from bs4 import BeautifulSoup
import sgzip
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pizzashoppe_com')



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url = "https://pizzashoppe.com"
    # conn = http.client.HTTPSConnection("guess.radius8.com")
 
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 80
    coords = search.next_coord()
    # search.current_zip """"""""==zip
    while coords:
        result_coords = []
        url = "https://pizzashoppe.com/wp-admin/admin-ajax.php"
        payload = 'action=get_stores&lat='+str(coords[0])+'&lng='+str(coords[1])+'&radius=200&categories%5B0%5D='
        # payload="action=get_stores&lat=39.20502279999999&lng=-94.70706159999999&radius=100&categories%5B0%5D="
        headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }
        response = session.post( url, headers=headers, data = payload).json()
        for val in response:
            store_number = response[val]['ID']
            location_name = response[val]['na']
            page_url = response[val]['gu']
            st = response[val]['st']
            city = response[val]['ct']
            zip1 = response[val]['zp']
            country = "US"
            latitude = response[val]['lat']
            state = response[val]['rg']
            longitude = response[val]['lng']
            phone = response[val]['te']
            hour=''
            hour1 =''
            try:
                hour =" ".join(list( BeautifulSoup(session.get(page_url).text, 'html.parser').find("div",{"class":"store_locator_single_opening_hours"}).stripped_strings))
            except:
                hour=''
            try:
                hour1 =" ".join(list( BeautifulSoup(session.get(page_url).text, 'html.parser').find("div",{"class":"store_locator_single_opening_hours2"}).stripped_strings))
            except:
                hour1=''
            hours_of_operation =hour+ ' '+hour1
            locator_domain = base_url
            street_address = st
            country_code = country
            store_number = "<MISSING>"
            location_type = ''
            result_coords.append((latitude,longitude))
            store = []
            hh= hours_of_operation.split("Opening Hours")[1:]
            if len(hh)==2:
                hours_of_operation = hh[0]
            else:
                hours_of_operation =  hh[0]
            # logger.info(hours_of_operation)
            
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city.strip() if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip1 if zip1 else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation.replace("Opening Hours",' ').replace("o'Clock",'').strip() if hours_of_operation else '<MISSING>')
            # logger.info(hours_of_operation.replace("Opening Hours",' ').replace("o'Clock",'').strip())
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store
            
        if len(response) < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(response) == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
