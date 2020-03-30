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
    base_url = "https://www.lawlersbarbecue.com"
    r = session.get("https://www.lawlersbarbecue.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    geo_object = {}
    for location in soup.find_all("div",{'class':"row sqs-row"}):
        if location.find("strong") == None:
            continue
        if location.find("iframe") == None:
            continue
        geo_object[location.find("strong").text.split(" -")[0].lower()] = location.find("iframe")["src"]
    for script in soup.find_all("script",{"type":'application/ld+json'}):
        if '"location":' in script.text:
            location_list = json.loads(script.text)["location"]
            for store_data in location_list:
                store = []
                store.append("https://www.lawlersbarbecue.com")
                store.append(store_data["name"])
                if " - " in store_data["name"]:
                    store_data["name"] = store_data["name"].split(" - ")[1]
                store.append(store_data["address"]["streetAddress"])
                store.append(store_data["address"]["addressLocality"])
                store.append(store_data["address"]["addressRegion"])
                store.append(store_data["address"]["postalCode"])
                store.append("US")
                store.append("<MISSING>")
                store.append(store_data["telephone"])
                store.append("law lers barbecue")
                if "!3d" in geo_object[store_data["name"].lower()]:
                    store.append(geo_object[store_data["name"].lower()].split("!3d")[1].split("!")[0])
                    store.append(geo_object[store_data["name"].lower()].split("!2d")[1].split("!")[0])
                else:
                    store.append(geo_object[store_data["name"].lower()].split("!1d")[1].split("!")[0])
                    store.append(geo_object[store_data["name"].lower()].split("!2d")[1].split("!")[0])
                del geo_object[store_data["name"].lower()]
                store.append(" ".join(store_data["openingHours"]))
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
