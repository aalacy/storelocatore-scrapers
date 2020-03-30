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
    base_url = "http://nogrease.com"
    r = session.get("http://nogrease.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"col-md-4 center"}):
        address = list(location.find("address").stripped_strings)
        hours = list(location.find_all("address")[1].stripped_strings)
        if "Store Hours" in hours:
            store_hours = " ".join(hours)
        else:
            store_hours = "<MISSING>"
        store = []
        store.append("http://nogrease.com")
        store.append(address[0])
        if len(address[2].split(",")) == 2:
            store.append(address[1])
            store.append(address[2].split(",")[0])
            store.append(address[2].split(",")[-1].split(" ")[-2])
            store.append(address[2].split(",")[-1].split(" ")[-1])
        elif len(address[2].split(" ")) == 3:
            store.append(address[1])
            store.append(address[2].split(" ")[0])
            store.append(address[2].split(" ")[-2])
            store.append(address[2].split(" ")[-1])
        else:
            store.append(address[0])
            store.append(address[1].split(",")[0])
            store.append(address[1].split(",")[-1].split(" ")[-2])
            store.append(address[1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(address[-1] if "Coming" not in address[-1] else "<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(store_hours)
        store.append("http://nogrease.com/locations")
        store = [x.replace("–","-") for x in store]
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
