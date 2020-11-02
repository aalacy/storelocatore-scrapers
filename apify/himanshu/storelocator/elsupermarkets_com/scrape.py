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
    return_main_object = []
    r = session.post("https://mallmotion.com:3033/api/v1/searchmall?checking=true&device_type=web&lang_id=en&latitude=33.89777370000001&longitude=-118.1649291&radius=100&wuid=4934ffb38c447169747548a2dcb7e397",verify=False)
    data = r.json()
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://elsupermarkets.com")
        store.append(store_data["name"])
        store.append(store_data["address"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data["id"])
        store.append(store_data["phone_no"])
        store.append("el super")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        if store_data["monday_start"] and store_data["monday_start"] != "":
            hours = hours + " Monday open time " + store_data["monday_start"] +" Monday close time " + store_data["monday_end"] + " "
        if store_data["tuesday_start"] and store_data["tuesday_start"] != "":
            hours = hours + " tuesday open time " + store_data["tuesday_start"] +" tuesday close time " + store_data["tuesday_end"] + " "
        if store_data["wednesday_start"] and store_data["wednesday_start"] != "":
            hours = hours + " wednesday open time " + store_data["wednesday_start"] +" wednesday close time " + store_data["wednesday_end"] + " "
        if store_data["thursday_start"] and store_data["thursday_start"] != "":
            hours = hours + " thursday open time " + store_data["thursday_start"] +" thursday close time " + store_data["thursday_end"] + " "
        if store_data["friday_start"] and store_data["friday_start"] != "":
            hours = hours + " friday open time " + store_data["friday_start"] +" friday close time " + store_data["friday_end"] + " "
        if store_data["saturday_start"] and store_data["saturday_start"] != "":
            hours = hours + " saturday open time " + store_data["saturday_start"] +" saturday close time " + store_data["saturday_end"] + " "
        if store_data["sunday_start"] and store_data["sunday_start"] != "":
            hours = hours + " sunday open time " + store_data["sunday_start"] +" sunday close time " + store_data["sunday_end"] + " "
        if hours == "":
            hours = "<MISSING>"
        store.append(hours if hours != "" or hours != None else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
