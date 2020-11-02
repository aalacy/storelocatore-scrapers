import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "https://www.wingsetc.com"
    r = session.get('https://wingsetc.com/wp-admin/admin-ajax.php?action=store_search&lat=41.07927&lng=-85.13935&max_results=100000&search_radius=1000&autoload=1')
    data = r.json()
    address = []
    hours_of_operation = "<MISSING>"
    for i in data:
        location_name = i['store']
        street_address = i['address']+""+i['address2']
        city = i['city']
        state = i['state']
        zipp = i['zip']
        phone = i['phone']
        latitude = i['lat']
        longitude = i['lng']
        store_number = i['store_number']
        country_code = i['country']
        location_type = "<MISSING>"
        page_url = i['url']
        hours_of_operation = str(i['hours']).replace("<ul><li><strong>","").replace('</strong> <time>'," - ").replace("</time></li><li><strong>",", ").replace("</time></li></ul>","")
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
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        # store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in address :
            continue
        address.append(store[2])
        if "Coming Soon!" in location_name:
            continue
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
