import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.diptyqueparis.com"
    address = ''
    r = session.get("https://www.diptyqueparis.com/en_eu/stockists/ajax/stores?_=1591599575723",headers=headers).json()
    for i in r:
        street_address1 = (i['country'])
        if "US" in street_address1:
            store_number = (i['stockist_id'])
            country_code = (i['country'])
            street_address = (i['address'])
            city = (i['city'])
            state = (i['region'])
            zipp =(i['postcode'])
            latitude = (i['latitude'])
            longitude =(i['longitude'])
            page_url=("https://www.diptyqueparis.com/en_eu/stores/"+i['link'])
            phone = (i['phone'])
            location_type = (i['type'])
            location_name = (i['name'])
            hours_of_operation = (i['schedule'])
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else"<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append(location_type if location_type else "<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation.replace('\\n'," ").split("Exceptional ")[0] if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            yield store 
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
