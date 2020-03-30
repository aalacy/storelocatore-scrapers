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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.fivestarfoodmart.com"
    r = session.get(base_url+"/locations")
    soup = BeautifulSoup(r.text,"lxml")
    location_phone = {}
    for location in soup.find_all("div",{"class":"location-block"}):
        location_id = location.find("a").text.split("#")[1]
        location_details = list(location.stripped_strings)
        location_phone[location_id] = location_details[-1]
    scripts = soup.find_all("script")
    return_main_object = []
    scripts = soup.find_all("script")
    for script in scripts:
        if "var wpgmaps_localize_marker_data" in script.text:
            location_list = json.loads(script.text.split("var wpgmaps_localize_marker_data = ")[1].split("};")[0] + "}")["1"]
            for key in location_list:
                store_data = location_list[key]
                store_data["address"] = store_data["address"].split(", USA")[0]
                store = []
                store.append("https://www.fivestarfoodmart.com")
                title = store_data["address"].split(",")[-2] + " Store " + store_data["title"].split(" ")[1]
                store.append(title)
                store.append(store_data["address"].split(",")[0])
                store.append(store_data['address'].split(",")[1])
                store.append(store_data['address'].split(",")[-1])
                store.append("<MISSING>")
                store.append("US")
                store.append(store_data["title"].split("#")[1])
                store.append(location_phone[store[-1]] if store[-1] in location_phone else "<MISSING>")
                store.append("five star")
                store.append(store_data["lat"])
                store.append(store_data["lng"])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
