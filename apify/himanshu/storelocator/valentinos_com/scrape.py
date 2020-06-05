import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
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
    base_url = "https://valentinos.com"
    address = []
    r = session.get("https://valentinos.com/wp-json/wp/v2/locations/?per_page=100").json()
    for i in r:
        data = (i['post_meta_fields']['maps_location']['address'])
        country_code = (data.split(",")[-1].strip())
        street_address= " ".join(data.split(",")[:-3])
        city = (data.split(",")[-3])
        state = (data.split(",")[-2].replace('68516',"").strip())
        latitude = (i['post_meta_fields']['maps_location']['lat'])
        longitude =(i['post_meta_fields']['maps_location']['lng'])
        zipp = i['post_meta_fields']['address_zip'][0]
        phone = (i['post_meta_fields']['phone'][0])
        hours_of_operation  =" ".join( list(BeautifulSoup(i['post_meta_fields']['hours'][0],'lxml').stripped_strings)).replace("\r\n"," ").split("Dining Room")[0].split("Buffet")[0].split('Party Rooms')[0]
        location_name = i["slug"]
        page_url = i['link']
        store_number = i['id']
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
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation.replace('Carryout & Delivery ','') if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        if store[2] in address :
            continue
        address.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
