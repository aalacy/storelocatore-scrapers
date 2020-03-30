import csv
from sgrequests import SgRequests
from datetime import datetime
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://cbna.com"
    r = session.get(base_url + "/locations")
    soup = BeautifulSoup(r.text,"lxml")
    scripts = soup.find_all("script")
    return_main_object = []
    data = json.loads(soup.find("locations")["location-data"])["locations"]
    for current_store in data:
        store = []
        store.append("https://cbna.com")
        store.append(current_store["title"])
        store.append(current_store["address"]["street1"])
        store.append(current_store["address"]["city"])
        store.append(current_store["address"]["state"])
        store.append(current_store["address"]["zip"])
        store.append("US")  
        store.append(current_store["id"])
        store.append(current_store["branchPhoneNumber"] if "branchPhoneNumber" in current_store and current_store["branchPhoneNumber"] else "<MISSING>")
        store.append("<MISSING>")
        store.append(current_store["address"]["lat"])
        store.append(current_store["address"]["lng"])
        hours = ""
        if "branchLobbyHours" in current_store:
            store_hours = current_store["branchLobbyHours"]
            for key in store_hours:
                if store_hours[key]["open"] == None and store_hours[key]["close"] == None:
                    continue
                hours = hours + " open " + datetime.strptime(store_hours[key]["open"]["date"].split(" ")[1][0:8] , "%H:%M:%S").strftime("%I:%M %p") + " close " + datetime.strptime(store_hours[key]["close"]["date"].split(" ")[1][0:8] , "%H:%M:%S").strftime("%I:%M %p")
        elif "notes" in current_store:
            hours = current_store["notes"][0]
        store.append(hours if hours != "" else "<MISSING>")
        store.append("<MISSING>")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
