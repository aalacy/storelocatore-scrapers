import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://find.cashamerica.us"
    r = session.get("http://find.cashamerica.us/js/controllers/StoreMapController.js")
    key = r.text.split("&key=")[1].split('");')[0]
    return_main_object = []
    page = 0
    while True:
        page = page + 1
        location_request = session.get("http://find.cashamerica.us/api/stores?p="+str(page) + "&s=10&lat=40.7128&lng=-74.006&d=2019-07-16T05:32:30.276Z&key="+ str(key))
        data = location_request.json()
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
            store.append(store_data["address"]["zipCode"])
            store.append("US")
            store.append(store_data["storeNumber"])
            store.append(store_data["phone"])
            store.append("cash america")
            store.append(store_data['latitude'])
            store.append(store_data['longitude'])
            hours_request = session.get("http://find.cashamerica.us/api/stores/"+ str(store_data["storeNumber"]) + "?key="+key)
            hours_details = hours_request.json()["weeklyHours"]
            hours = ""
            for k in range(len(hours_details)):
                if hours_details[k]["openTime"] != "Closed":
                    hours = hours + " " +hours_details[k]["weekDay"] + " " + hours_details[k]["openTime"] + " " + hours_details[k]["closeTime"] + " "
            store.append(hours if hours != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
