import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import requests
import json
import time
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    
    r = requests.get("http://find.cashamerica.us/js/controllers/StoreMapController.js")
    key = r.text.split("&key=")[1].split('");')[0]
    addresses = []
    page = 1
    while True:
        location_request = requests.get("http://find.cashamerica.us/api/stores?p="+str(page) + "&s=10&lat=40.7128&lng=-74.006&d=2019-07-16T05:32:30.276Z&key="+ str(key), headers = headers, verify = False)
        json_data = location_request.json()
        if "message" in json_data:
            break
        for data in json_data:
        
            store = []
            store.append("http://find.cashamerica.us")
            store.append(data["brand"])
            store.append(data["address"]["address1"] +data["address"]["address2"] if data["address"]["address2"] != None else data["address"]["address1"])
            store.append(data["address"]["city"])
            store.append(data["address"]["state"])
            store.append(data["address"]["zipCode"] if data["address"]["zipCode"] else "<MISSING>")
            store.append("US")
            store.append(data["storeNumber"])
            store.append(data["phone"])
            store.append(data["brand"].replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","").replace("#","").strip())
            store.append(data['latitude'])
            store.append(data['longitude'])
            hours_request = requests.get("http://find.cashamerica.us/api/stores/"+ str(data["storeNumber"]) + "?key="+key)
            hours_details = hours_request.json()["weeklyHours"]
            hours = ""
            for k in range(len(hours_details)):
                if hours_details[k]["openTime"] != "Closed":
                    hours = hours + " " +hours_details[k]["weekDay"] + " " + hours_details[k]["openTime"] + " " + hours_details[k]["closeTime"] + " "
            store.append(hours if hours != "" else "<MISSING>")
            store.append("<INACCESSIBLE>")
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # print(store)
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
