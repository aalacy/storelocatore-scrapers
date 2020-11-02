import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    return_main_object = []
    addresses = []
    cords = sgzip.coords_for_radius(200)
    for cord in cords:
        base_url = "https://mobiloil.com"
        r = requests.get("https://mobiloil.com/api/v1/locations/search?q=nearby(" + str(cord[0]) + "," + str(cord[1]) + ",200)&s=*,__Distance&l=R,A,M&t=100000",headers=headers)
        data = r.json()
        for store_data in data:
            store = []
            store.append("https://mobiloil.com")
            store.append(store_data["Name"])
            store.append(store_data["Address1"] + store_data["Address2"] if "Address2" in store_data else store_data["Address1"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["City"])
            store.append(store_data["State"])
            store.append(store_data["PostalCode"])
            store.append("US")
            store.append(store_data["Id"])
            store.append(store_data["Phone"] if store_data["Phone"] != "" and store_data["Phone"] != None else "<MISSING>")
            store.append("mobil oil")
            if store_data["Type"] == "R":
                store[-1] = store[-1] + " Retailers"
            elif store_data["Type"] == "A":
                store[-1] = store[-1] + " Service centers"
            elif store_data["Type"] == "M":
                store[-1] = store[-1] + " Service centers"
            store.append(store_data["Coords"]["Lat"])
            store.append(store_data["Coords"]["Long"])
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
