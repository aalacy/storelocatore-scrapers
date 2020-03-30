import csv
import sgrequests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
from sgrequests import SgRequests

session = SgRequests()

session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation" , "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url= "https://api.morrisons.com/location/v2//stores?apikey=kxBdM2chFwZjNvG2PwnSn3sj6C53dLEY&distance=5000000&lat=51.49919128417969&limit=500000&lon=-0.09428299963474274&offset=0&storeformat=supermarket"
    r = session.get(base_url, headers=headers).json()

    for d in r['stores']:
        location_name = (d['storeName'])
        if "Gibraltar" in location_name:
            continue
        # print(latitude)
        m = d['address']['addressLine1']
        p = d['address']['addressLine2']
        street_address = (m + p).replace("      ","")
        state = d['address']['county']
        city= d['address']['city']
        zipp = d['address']['postcode']
        country_code = d['address']['country']
        phone = d['telephone']
        latitude =  d['location']['latitude']
        longitude =  d['location']['longitude']
        store_number = d['name'] 
        location_type = d['storeFormat']
        url = "https://my.morrisons.com/storefinder/"+str(store_number)
        hours_of_operation =''
        h1  = (d['openingTimes'])
        for p in h1:
            hours_of_operation  = (hours_of_operation +' '+p + ' ' +h1[p]['open']+' '+h1[p]['close']).strip()
        store = []
        store.append("https://morrisons.com/")
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state.upper() if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>' )
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>' )
        store.append(url)
        
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
