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
    base_url = "https://www.cardsmart.com"
    r = session.get("https://www.mira-labs.net/get_user_locations_map/?instanceID=338377d9-797b-4382-8235-f418c4032fea&compID=comp-j6cb5nsq&_=1564138585654")
    data = r.json()["locations"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.cardsmart.com")
        store.append(store_data['name'])
        if len(store_data["formatted_address"].split(",")) == 1:
            store.append(" ".join(store_data["formatted_address"].split(" ")[0:-3]))
            store.append(store_data["formatted_address"].split(" ")[-3])
            store.append(store_data["formatted_address"].split(" ")[-2])
            store.append(store_data["formatted_address"].split(" ")[-1])
        else:
            if len(store_data["formatted_address"].split('.')) > 1:
                store.append(store_data["formatted_address"].split(',')[0].split(".")[0])
                store.append(store_data["formatted_address"].split(',')[0].split(".")[-1])
            else:
                store.append(store_data["formatted_address"].split(",")[0])
                store.append(store_data["formatted_address"].split(",")[1])
            if len(store_data['formatted_address'].split(",")) < 4:
                store.append(store_data['formatted_address'].split(",")[-1].split(" ")[-2].replace(".",""))
                store.append(store_data['formatted_address'].split(",")[-1].split(" ")[-1])
                if store[-1] == "NY":
                    store[-1] = "<MISSING>"
            else:
                store.append(store_data['formatted_address'].split(",")[-2])
                store.append(store_data['formatted_address'].split(",")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(store_data["tel"] if store_data["tel"] != "" else "<MISSING>")
        store.append("card smart")
        store.append(store_data['latitude'])
        store.append(store_data['longitude'])
        store.append(store_data["opening_hours"] if store_data['opening_hours'] != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
