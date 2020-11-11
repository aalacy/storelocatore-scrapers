import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import unicodedata

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.kiyonna.com"
    r = requests.get("https://www.kiyonna.com/GMAP.html")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for store_data in soup.find_all("div",{"class":"icon"}):
        if "USA" not in store_data["address1"] and "Canada" not in store_data["address1"] and "United States" not in store_data["address1"]:
            continue
        store = []
        store.append("https://www.kiyonna.com")
        store.append(store_data["name"])
        store.append(store_data["address"] if store_data["address"] != " " else "<MISSING>")
        store.append(store_data["address1"].split(",")[0])
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        if "USA" in store_data["address1"] or "United States" in store_data["address1"]:
            store.append("US")
        if "Canada" in store_data["address1"]:
            store.append("CA")
        store.append(store_data["item"])
        store.append(store_data["phone"].replace("&#40;","(").replace("&#41;",")"))
        if store[-1] == "":
            store[-1] = "<MISSING>"
        store.append("kiyonna")
        store.append(store_data['lat'])
        store.append(store_data['lng'])
        hours = ""
        hours = store_data.parent.parent.find("span",{"class":"u-shown gmap--store-info"}).find_all("span",{'class':"u-shown"})[-1].text
        if "Toll" in hours:
            hours = "<MISSING>"
        if len(hours) == 14 and hours.count("-") == 3:
            hours = "<MISSING>"
        store.append(hours if store[-4] != hours and "hours" not in hours.lower() else "<MISSING>")
        store.append("https://www.kiyonna.com/GMAP.html")
        store.append(store_data["address1"].split(",")[1])
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.strip() if type(x) == str else x for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
