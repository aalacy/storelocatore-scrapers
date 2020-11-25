import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    adressess = []
    MAX_RESULTS = 100
    MAX_DISTANCE = 50
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    while zip_code:
        result_coords =[]
        base_url = "https://www.tiresplus.com"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',"Content-Type": "application/json; charset=utf-8"}
        try:
            r = session.get('https://www.tiresplus.com/bsro/services/store/location/get-list-by-zip?zipCode='+str(zip_code),headers=headers).json()['data']['stores']
        except KeyError:
            pass
        for loc in r:
            name=loc['storeName']
            address=loc['address']
            city=loc['city']
            lat=loc['latitude']
            lng=loc['longitude']
            storeno=loc['storeNumber']
            phone=loc['phone']
            store_type = loc['storeType']
            state=loc['state']
            zip=loc['zip']
            page_url = loc['localPageURL']
            country="US"
            hour=''
            for hr in loc['hours']:
                hour+=hr['weekDay']+":"+hr['openTime']+"-"+hr['closeTime']+", "
            hour = hour.replace("07:30-07:30","07:30-18:30")
            store=[]
            store.append(base_url)
            store.append(name if name else "<MISSING>")
            store.append(address if address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zip if zip else "<MISSING>")
            store.append(country if country else "<MISSING>")
            store.append(storeno if storeno else "<MISSING>")
            store.append(phone if phone else "<MISSING>")
            store.append(store_type)
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour.strip().rstrip(",") if hour.strip().rstrip(",") else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in adressess:
                continue
            adressess.append(store[2])
            yield store
        if len(r) < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif len(r) == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
