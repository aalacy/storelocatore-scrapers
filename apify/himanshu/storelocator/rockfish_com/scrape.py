import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://www.rockfish.com"
    r = session.get(base_url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for link in soup.find("ul",{"class":"mega-sub-menu"}).find_all("a",{"class":"mega-menu-link"}):
        page_url = link['href']
        r1= session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        pp = list(soup1.find("rs-zone",{"class":"rev_row_zone_top"}).stripped_strings)
        location_name = pp[0]
        addr = pp[1].split(",")
        street_address = addr[0]
        city = addr[1].strip()
        state = addr[2].strip().split(" ")[0]
        zipp = addr[2].strip().split(" ")[1]
        phone = pp[-1]
        hours_of_operation = pp[2]
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append("US")
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append("Rockfish Seafood Grill")
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
