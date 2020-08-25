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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
    }
    base_url = "https://www.workngear.com"
    r = session.get("https://www.workngear.com/store-locator",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    locations = soup.find_all("div",{"class":"results-stores"})
    return_main_object = []
    for location in soup.find_all("ul",{'class':"col-lg-4 col-sm-6 col-xs-12 storeDetails"}):
        address = list(location.find("div",{"class":'store-locator-address'}).stripped_strings)
        phone = list(location.find("div",{"class":'store-locator-pno'}).stripped_strings)[1]
        hours = " ".join(list(location.find("div",{"class":'store-locator-hours'}).stripped_strings)).replace("View More View Less","").replace('Store Hours: ','')
        geo_location = location.find("a",{"class":"button normal blue small"})['href']
        store = []
        store.append("https://www.workngear.com")
        store.append(address[0])
        store.append(address[1])
        store.append(address[0].split(",")[0] if len(address[0].split(",")) == 2 else "<MISSING>")
        store.append(address[0].split(",")[1] if len(address[0].split(",")) == 2 else "<MISSING>")
        store.append(address[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(geo_location.split("//")[2].split(",")[0])
        store.append(geo_location.split("//")[2].split(",")[1].split("/")[0])
        store.append(hours)
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)

scrape()
