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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    cords = sgzip.coords_for_radius(100)
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    for cord in cords:
        base_url = "https://can-am.brp.com"
        r = session.get("https://can-am.brp.com/rest/dealerlocator/search?latitude=" + str(cord[0]) + "&longitude=" + str(cord[1]) + "&radius=200&country_code=US&language_code=en&zip_code=&product_line=roadster",headers=headers)
        for store_data in r.json()["nearbyDealers"]:
            if store_data["country"] != "CA" and store_data["country"] != "US":
                continue
            store = []
            store.append("https://can-am.brp.com")
            store.append(store_data["name"])
            store.append(store_data["streetAddress"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["city"])
            store.append(store_data["state"])
            store.append(store_data["zipCode"])
            store.append(store_data["country"])
            store.append(store_data["dealerNumber"])
            store.append(store_data["phoneNumber"] if store_data["phoneNumber"] != "" and store_data["phoneNumber"] != None else "<MISSING>")
            store.append("can-am")
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            hours = ""
            days = {0:"Mon",1:"Tue",2:"Wed",3:"Thu",4:"Fri",5:"Sat",6:"Sun"}
            if store_data["rentalHours"] != []:
                hours = hours + " rental Hours "
                for i in range(len(store_data["rentalHours"])):
                    hours = hours + " " + days[i] + " " + store_data["rentalHours"][i]
            if store_data["serviceHours"] != []:
                hours = hours + " service Hours "
                for i in range(len(store_data["serviceHours"])):
                    hours = hours + " " + days[i] + " " + store_data["serviceHours"][i]
            if store_data["showroomHours"] != []:
                hours = hours + " showroom Hours "
                for i in range(len(store_data["showroomHours"])):
                    hours = hours + " " + days[i] + " " + store_data["showroomHours"][i]
            store.append(hours if hours != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
