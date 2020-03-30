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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://luckywishbone.com"
    r = session.get("https://luckywishbone.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "var maplistScriptParamsKo = " in script.text:
            location_list = json.loads(script.text.split('var maplistScriptParamsKo = ')[1].split("};")[0] + "}")["KOObject"][0]["locations"]
            for store_data in location_list:
                location_details = list(BeautifulSoup(store_data["description"],"lxml").stripped_strings)
                store = []
                store.append("https://luckywishbone.com")
                store.append(store_data["title"])
                store.append(location_details[0])
                store.append(location_details[1].split(",")[0])
                store.append(location_details[1].split(",")[1].split(" ")[-2])
                store.append(location_details[1].split(",")[1].split(" ")[-1])
                store.append("US")
                store.append(store_data["cssClass"].split("-")[1])
                store.append(location_details[2].replace("Phone",""))
                store.append("lucky wishbone")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
