import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import datetime

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
    today = datetime.date.today().strftime("%Y-%m-%d")
    year = datetime.date.today().strftime("%Y")
    return_main_object = []
    zips = sgzip.for_radius(200)
    addresses = []
    for zip_code in zips:
        headers = {
            "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
        }
        base_url = "https://www.genesis.com"
        r = session.get("https://www.genesis.com/content/genesis/us/en/services/dealerservice.js?countryCode=en-US&servicetype=new&vehicleName=all&year=" + str(year) + "&zipCode="+ str(zip_code) + "&noOfResults=100000&refreshToken=" + str(today),headers=headers)
        data = r.json()["dealers"]
        for store_data in data:
            store = []
            store.append("https://www.genesis.com")
            store.append(store_data["dealerNm"])
            store.append(store_data["address1"] + store_data["address2"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["city"])
            store.append(store_data["state"])
            store.append(store_data["zipCd"])
            store.append("US")
            store.append(store_data["dealerCd"])
            store.append(store_data["phone"] if store_data["phone"] == "" else "<MISSING>")
            store.append("genesis")
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            hours = ""
            store_hours = store_data["operations"]
            for location_hour in store_hours:
                hours = hours + " " + location_hour["day"] + " " + location_hour["hour"]
            store.append(hours if hours != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
