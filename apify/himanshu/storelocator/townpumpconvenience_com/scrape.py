import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.townpump.com"
    r = requests.get("https://www.townpump.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    web_id = soup.find("script",{"id":"storelocatorscript"})["data-uid"]
    location_request = requests.get("https://cdn.storelocatorwidgets.com/json/" + web_id , headers=headers)
    data = json.loads(location_request.text.split("slw(")[1].split("]})")[0] + "]}")["stores"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.townpump.com")
        store.append(store_data['name'])
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("US")
        store.append(store_data["storeid"])
        store.append(store_data["data"]["phone"] if "phone" in store_data["data"] and store_data["data"]["phone"] != "" and store_data["data"]["phone"] != None else "<MISSING>")
        store.append("town  pump")
        store.append(store_data["data"]["map_lat"])
        store.append(store_data["data"]["map_lng"])
        store.append("<MISSING>")
        store.append(store_data["data"]["address"])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
