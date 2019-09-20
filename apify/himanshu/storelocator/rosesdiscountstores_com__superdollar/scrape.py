import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    r = requests.get("https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?northeast=54.813172%2C-46.350462&southwest=-4.17774%2C-149.147167")
    data = r.json()["locations"]
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.rosesdiscountstores.com/#superdollar")
        store.append(store_data["name"])
        store.append(" ".join(store_data["address"].split(",")[0:-3]))
        if store[-1] == "":
            store[-1] = store_data["address"].split(",")[0]
        store.append(store_data["city"] if store_data["city"] else store_data["address"].split(",")[1])
        store.append(store_data["region"])
        store.append(store_data["postcode"] if store_data["postcode"] != "" else store_data["address"].split(",")[-2].split(" ")[-1])
        if len(store[-1]) <= 3 or len(store[-1]) >=7:
            store[-1] = "<MISSING>"
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["contacts"]["con_wg5rd22k"]["text"])
        store.append("roses")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        hours = ""
        if type(store_data["hours"]) == dict:
            for key in store_data["hours"]["hoursOfOperation"]:
                hours = hours + key + " " +store_data["hours"]["hoursOfOperation"][key].replace("-"," to ") + " "
        elif store_data["hours"] == "hrs_ywfef43p":
            hours = "mon 9 am to 9 pm tue 9 am to 9 pm wed 9 am to 9 pm thurs 9 am to 9 pm fri 9 am sat 9 am to 9pm sun 10 am to 8 pm"
        elif store_data["hours"] == "hrs_a4db656x":
            hours = "mon 9 am to 6 pm tue 9 am to 6 pm wed 9 am to 6 pm thurs 9 am to 6 pm fri 9 am sat 6 am to 9pm sun 12 am to 6 pm"
        else:
            hours = store_data["hours"]
        store.append(hours if hours else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()