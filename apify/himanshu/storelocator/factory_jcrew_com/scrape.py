import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    addresses =[]
    base_url = "https://factory.jcrew.com/"
    location_url ="https://stores.factory.jcrew.com/en/api/v2/stores.json"   
    r = session.get(location_url, headers=headers).json()
    for i in r['stores']:
        location_name = i['name']
        address_2 =  i['address_2']
        # address_2 = 
        if address_2!=None:
            street_address = i['address_1']+' '+i['address_2']
        else:
            street_address = i['address_1']   
        city = i['city']
        state = i['state']
        zipp = i['postal_code']
        store_number = i['id']
        country_code = i['country_code']
        phone = i['phone_number']
        latitude = i['latitude']
        longitude = i['longitude']
        k = i["url"]
        page_url = "https://stores.factory.jcrew.com/"+str(k)
        hr = []
        for h in i['regular_hour_ranges']:
            m = h['days']
            p = h['hours'].replace("&#8211; ","-").strip().lstrip()
            hours = hr.append(m+" "+p)
        hours_of_operation = " ".join(hr)
        store = []
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>")
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code)
        store.append(store_number if store_number else "<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>" )
        store.append(page_url if page_url else "<MISSING>" )
        for i in range(len(store)):
            if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize(
                        'NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–", "-") if type(x) ==
                     str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode(
                'ascii').strip() if type(x) == str else x for x in store]
        yield store
   
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
