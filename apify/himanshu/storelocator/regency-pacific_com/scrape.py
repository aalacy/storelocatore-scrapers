import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json

session = SgRequests()
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
        return_main_object = []
        addresses = []
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            'Connection': 'keep-alive',
            }
        base_url = "https://www.regency-pacific.com"
        r1 = session.get("https://g5-geo-service.herokuapp.com/clients/g5-c-ifyj3t6d-regency-pacific-management-client/location_search.json?search=21216&radius=100&lat=39.31&lon=-76.66", headers= headers).json()
        for i in r1["locations"]:
            store_number = (i['id'])
            location_name = i['name']
            street_address = i['street_address_1']
            city = i['city']
            state = i['state']
            zipp = i['postal_code']
            latitude= i['latitude']
            longitude= i['longitude']
            page_url= i['home_page_url']
            phone= i['phone_number']
            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append(store_number)
            store.append(phone if phone else "<MISSING>" )
            store.append("<MISSING>")
            store.append( latitude if latitude else "<MISSING>")
            store.append( longitude if longitude else "<MISSING>")
            store.append("<MISSING>")
            store.append(page_url)
            if store[2] in addresses :
                continue
            addresses.append(store[2])
            yield store
def scrape():
 data = fetch_data()
 write_output(data)
scrape()
