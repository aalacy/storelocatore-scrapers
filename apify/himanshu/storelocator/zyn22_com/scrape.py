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
    base_url = "https://www.zyn22.com"
    r = session.get("https://www.zyn22.com/contact/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    box = soup.find_all("div",{"class":"elementor-widget-wrap"})[5:7]
    for i in box:
        dl = list(i.stripped_strings)
        location_name = dl[1]
        street_address = dl[-1].split("\n")[0]
        addr = dl[-1].split("\n")[1]
        city = addr.split(",")[0]
        state = addr.split(",")[1].strip().split(" ")[0]
        zipp = addr.split(",")[1].strip().split(" ")[1]
        phone = dl[6]
        if location_name == "Fort Worth Studio":
            page_url = "https://www.zyn22.com/home-fortworth/"
        else:
            page_url = "https://www.zyn22.com/home-dallas/"
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
        store.append("ZYN22")
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append(page_url)
        store = [x.strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
