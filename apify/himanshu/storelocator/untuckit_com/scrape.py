import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.untuckit.com"
    r = requests.get("https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/5048/stores.js")
    data = r.json()["stores"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.untuckit.com")
        store.append(store_data['name'])
        store_data["address"] = store_data["address"].split(", USA")[0]
        if len(store_data["address"].split(",")) > 1:
            store.append(" ".join(store_data["address"].split(",")[0:-2]))
            store.append(store_data["address"].split(",")[-2])
            if len(store_data["address"].split(",")[-1].split(" ")[-1]) == 5:
                store.append(store_data["address"].split(",")[-1].split(" ")[-2])
                store.append(store_data["address"].split(",")[-1].split(" ")[-1])
                store.append("US")
            else:
                store.append(store_data["address"].split(",")[-1].split(" ")[1])
                store.append(" ".join(store_data["address"].split(",")[-1].split(" ")[2:]))
                store.append("CA")
        else:
            if len(store_data["address"].split(" ")[-1]) == 5:
                store.append(" ".join(store_data["address"].split(" ")[:-3]))
                store.append(store_data["address"].split(" ")[-3])
                store.append(store_data["address"].split(" ")[-2])
                store.append(store_data["address"].split(" ")[-1])
                store.append("US")
            else:
                store.append(" ".join(store_data["address"].split(" ")[:-4]))
                store.append(store_data["address"].split(" ")[-4])
                store.append(store_data["address"].split(" ")[-3])
                store.append(" ".join(store_data["address"].split(" ")[-1:-3]))
                store.append("CA")
        if store_data["address"].count("New York") == 2:
            store[-3] = "New York"
            store[-4] = "New York"
        store.append(store_data["id"])
        store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
        store.append("untuck it " + store_data["category"])
        store.append(store_data['latitude'])
        store.append(store_data['longitude'])
        store.append(store_data["description"] if store_data["description"] != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
