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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.dolcegabbana.com"
    r = session.get("https://www.dolcegabbana.com/store-locator/wp-content/uploads/stores-en.json",headers=headers)
    data = r.json()
    return_main_object = []
    for key in data:
        if "title" not in data[key]:
            continue
        if data[key]["title"] == "United States":
            current_country = "US"
        elif data[key]["title"] == "Canada":
            current_country = "CA"
        else:
            continue
        for state in data[key]["items"]:
            for location in data[key]["items"][state]["items"]:
                store_data = data[key]["items"][state]["items"][location]
                name = store_data["title"]
                if "Opening Soon".lower() in store_data["notes"].lower():
                    continue
                store = []
                store.append("https://www.dolcegabbana.com")
                store.append(store_data["title"] if store_data["title"] != "" else "<MISSING>")
                store.append(" ".join(list(BeautifulSoup(store_data["street_address"],"lxml").stripped_strings)) if store_data["street_address"] != "" else "<MISSING>")
                store.append(store_data["city"] if store_data["city"] != "" else "<MISSING>")
                store.append(store_data["state"] if store_data["state"] != "" else "<MISSING>")
                if current_country == "US":
                    store_data["zip_code"] = store_data["zip_code"].split(" ")[-1]
                store.append(store_data["zip_code"] if store_data["zip_code"] != "" else "<MISSING>")
                store.append(current_country)
                store.append(store_data["real_id"])
                store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
                store.append("<MISSING>")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                store.append("<MISSING>")
                for i in range(len(store)):
                    store[i] = store[i].replace('–',"-")
                store.append("<MISSING>")
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
