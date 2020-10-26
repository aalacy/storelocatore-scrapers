import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline= '') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    addressess = []
    locator_domain = "https://www.metrobyt-mobile.com/"
    r = session.get("https://www.metrobyt-mobile.com/api/v1/commerce/store-locator?address=10012&store-type=All&min-latitude=40.43781415437058&max-latitude=41.01752429929811&min-longitude=-73.62099509844096&max-longitude=-74.37571207957303", headers=headers).json()
    for dt in r:
        location_name = dt['name']
        street_address = dt['location']['address']['streetAddress']
        zipp = dt['location']['address']['postalCode']
        state = dt['location']['address']['addressRegion']
        city = dt['location']['address']['addressLocality']
        latitude = dt['location']['latitude']
        longitude = dt['location']['longitude']
        phone = dt['telephone']
        hours_of_operation=''
        for h in dt['openingHours']:
            hours_of_operation = ", ".join(h['days']) + ' ' + h['time']
        location_type=dt['type']
        page_url = ("https://www.metrobyt-mobile.com/storelocator/"+state.lower()+'/'+city.lower().replace(" ",'-')+'/'+street_address.lower().replace(" ",'-'))
        if len(zipp)==4:
            zipp = "0"+zipp
        if "Corporate Store" in location_type:
            continue
        # print(location_type)
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append('US')
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
    

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
