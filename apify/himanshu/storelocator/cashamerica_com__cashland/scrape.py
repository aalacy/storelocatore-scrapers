import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
import requests
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = "http://cashamerica.com/cashland"
    r = requests.get("http://find.cashamerica.us/js/controllers/StoreMapController.js")
    key = r.text.split("&key=")[1].split('");')[0]
    return_main_object = []
    page = 0
    address = []
    addresses = ''
    addresses = []
    for i in range(1,915):
        try:
            location_request = requests.get("http://find.cashamerica.us/api/stores?p="+str(i) + "&s=10&lat=40.7128&lng=-74.006&d=2019-07-16T05:32:30.276Z&key="+ str(key))
            data = location_request.json()
        except:
            pass
        #print("http://find.cashamerica.us/api/stores?p="+str(i) + "&s=10&lat=40.7128&lng=-74.006&d=2019-07-16T05:32:30.276Z&key="+ str(key))
        if "message" in data:
            if data["message"] == "An error has occurred.":
                break
        for i in range(len(data)):
            store_data = data[i]
            store = []
            store.append("http://find.cashamerica.us")
            store.append(store_data["brand"])
            store.append(store_data["address"]["address1"] +store_data["address"]["address2"] if store_data["address"]["address2"] != None else store_data["address"]["address1"])
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["state"])
            store.append(store_data["address"]["zipCode"] if store_data["address"]["zipCode"] else "<MISSING>")
            store.append("US")
            store.append(store_data["storeNumber"])
            store.append(store_data["phone"])
            store.append(store_data["brand"].replace("0","").replace("1","").replace("2","").replace("3","").replace("4","").replace("5","").replace("6","").replace("7","").replace("8","").replace("9","").replace("#","").strip())
            store.append(store_data['latitude'])
            store.append(store_data['longitude'])
            hours_request = requests.get("http://find.cashamerica.us/api/stores/"+ str(store_data["storeNumber"]) + "?key="+key)
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
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
