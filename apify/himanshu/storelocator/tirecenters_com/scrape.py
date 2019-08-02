import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    base_url = "ttp://tirecenters.com"
    data = "method=getDistribution&count=9999&lat=39.8282&lon=-98.5795"
    r = requests.post("http://tirecenters.com/modules/StoreLookup.cfc",data=data,headers=headers)
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("http://tirecenters.com")
        store.append(store_data["name"])
        store.append((store_data["address1"] + store_data["address2"]).strip())
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data["id"])
        current_store_data = "method=getDetail&storenum=" + str(store_data["dept_store"])
        if type(store_data["dept_store"]) == int:
            store_request = requests.post("http://tirecenters.com/modules/StoreLookup.cfc",data=current_store_data,headers=headers)
            store.append(store_request.json()["phone"] if "phone" in store_request.json() and store_request.json()["phone"] != "" and store_request.json()["phone"] != None else "<MISSING>")
        else:
            store.append("<MISSING>")
        store.append("tire centers")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append(store_data["hours"] + store_data["weekend_hours"] if store_data["hours"] + store_data["weekend_hours"] != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
