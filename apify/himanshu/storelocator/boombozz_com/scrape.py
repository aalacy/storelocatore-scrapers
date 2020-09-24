import csv
from bs4 import BeautifulSoup
import re
import json
import time
from sgrequests import SgRequests
session = SgRequests() 
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    address = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url = "https://boombozz.com/"
    location_url = "https://boombozz.com/wp-admin/admin-ajax.php?action=store_search&lat=38.23184&lng=-85.71014&max_results=25&search_radius=50&autoload=1"
    r = session.get(location_url,headers=headers)
    data = (r.json())
    for i in data:
        location_type = "BoomBozz"
        page_url_data  = (i['description'].split('https://boombozz.com/')[1].split('\" target=\"')[0])
        page_url = ("https://boombozz.com/"+str(page_url_data))
        r = session.get(page_url,headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        data = (soup.find("div",{"class":"hoursColumn"}))
        hours = (" ".join(list(data.stripped_strings)[0:]))
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(i['store'] if i['store'] else "<MISSING>") 
        store.append(i['address'] if i['address'] else "<MISSING>")
        store.append(i['city'] if i['city'] else "<MISSING>")
        store.append(i['state'] if i['state'] else "<MISSING>")
        store.append(i['zip'] if i['zip']  else "<MISSING>")
        store.append(i['country'] if i['country'] else "<MISSING>")
        store.append(i['id'] if i['id'] else"<MISSING>") 
        store.append(i['phone'] if i['phone'] else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(i['lat'] if i['lat'] else "<MISSING>")
        store.append(i['lng'] if i['lng'] else "<MISSING>")
        store.append(hours.replace("Bar Opens One Hour Later","") if hours else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in address :
            continue
        address.append(store[2])
        yield store 

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
