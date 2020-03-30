import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from datetime import datetime


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    cords = sgzip.coords_for_radius(200)
    for cord in cords:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
        # print("https://hancockwhitney-api-production.herokuapp.com/location?latitude=" + str(cord[0]) + "&locationTypes=atm,branch,business&longitude=" + str(cord[1]) + "&pageSize=100&radius=200&searchByState=&sort=distance&sortDir=-1")
        r = session.get("https://hancockwhitney-api-production.herokuapp.com/location?latitude=" + str(cord[0]) + "&locationTypes=atm,branch,business&longitude=" + str(cord[1]) + "&pageSize=100&radius=200&searchByState=&sort=distance&sortDir=-1",headers=headers)
        data = r.json()["data"]
        for store_data in data:
            store = []
            store.append("https://www.hancockwhitney.com")
            store.append(store_data["name"])
            store.append(store_data["address"]["street"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["state"])
            store.append(store_data["address"]["zip"])
            store.append("US")
            store.append("<MISSING>")
            store.append(store_data["phone"].replace("_","-") if "phone" in store_data and store_data["phone"] and store_data["phone"] != "TBD" else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["geo"]["coordinates"][1])
            store.append(store_data["geo"]["coordinates"][0])
            hours = ""
            for key in store_data:
                if "Hours" in key:
                    hours = hours + key + " " + store_data[key] + " "
            store.append(hours if hours else "<MISSING>")
            store.append("<MISSING>")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
