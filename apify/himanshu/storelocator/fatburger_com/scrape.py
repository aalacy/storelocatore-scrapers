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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://fatburger.com"
    r = session.get("https://locations.fatburger.com/locations.json")
    data = r.json()["locations"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        if store_data["loc"]["country"] == "US" or store_data["loc"]["country"] == "CA":
            store = []
            store_data = store_data["loc"]
            store.append("https://fatburger.com")
            store.append(store_data['name'])
            store.append(store_data["address1"] + store_data["address2"])
            store.append(store_data['city'])
            store.append(store_data['state'])
            store.append(store_data["postalCode"] if store_data["postalCode"] != None else "<MISSING>")
            store.append(store_data["country"])
            store.append(store_data["id"])
            if store_data["phone"]:
                store.append(store_data["phone"])
            else:
                store.append("<MISSING>")
            store.append("fast frame")
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            hours = ""
            open_hours = store_data["hours"]["days"]
            for k in range(len(open_hours)):
                if len(open_hours[k]["intervals"]) == 0:
                    continue
                if open_hours[k]["intervals"][0]["end"] == 0 and open_hours[k]["intervals"][0]["start"] == 0:
                    hours = hours + " " + open_hours[k]["day"] + " 24/7 "
                else:
                    hours = hours + " " + open_hours[k]["day"] + " " + str(open_hours[k]["intervals"][0]["start"]) + " " + str(open_hours[k]["intervals"][0]["end"])
            store.append(hours if hours != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
