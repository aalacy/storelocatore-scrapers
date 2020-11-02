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
    cords = sgzip.coords_for_radius(100)
    r = requests.get("https://www.benjaminmoore.com/en-us/store-locator",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for script in soup.find_all("script"):
        if "bmcApi" in script.text:
            api_url = script.text.split('bmcApi":')[1].split('",')[0].replace('"',"")
    for cord in cords:
        base_url = "https://www.benjaminmoore.com"
        r = requests.get(api_url + "/retailer/GetStoresByGeolocation?countryCode=en-us&latitude=" + str(cord[0]) + "&longitude=" + str(cord[1]) + "&radius=100",headers=headers)
        data = r.json()["data"]
        for store_data in data:
            if store_data["countryCode"] != "US" and store_data["countryCode"] != "CA":
                continue
            store = []
            store.append("https://www.benjaminmoore.com")
            store.append(store_data["storeName"])
            store.append(store_data["addressLine1"] + " " + store_data["addressLine2"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["city"])
            store.append(store_data["state"])
            store.append(store_data["zipCode"])
            store.append(store_data["countryCode"])
            store.append(store_data["storeNumber"])
            store.append(store_data["phone"] if store_data["phone"] != "" or store_data["phone"] != None else "<MISSING>")
            if store[-1] == "00000":
                store[-1] = "<MISSING>"
            store.append("benjamin moore")
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            hours = ""
            store_hours = store_data["hours"]
            hours = hours + " Monday " + store_hours['mondayOpen'] + " - " + store_hours["mondayClose"]
            hours = hours + " Tuesday " + store_hours['tuesdayOpen'] + " - " + store_hours["tuesdayClose"]
            hours = hours + " Wednesday " + store_hours['wednesdayOpen'] + " - " + store_hours["wednesdayClose"]
            hours = hours + " Thursday " + store_hours['thursdayOpen'] + " - " + store_hours["thursdayClose"]
            hours = hours + " Friday " + store_hours['fridayOpen'] + " - " + store_hours["fridayClose"]
            hours = hours + " Saturday " + store_hours['saturdayOpen'] + " - " + store_hours["saturdayClose"]
            hours = hours + " Saturday " + store_hours['sundayOpen'] + " - " + store_hours["sundayClose"]
            store.append(hours if hours != "" else "<MISSING>")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
