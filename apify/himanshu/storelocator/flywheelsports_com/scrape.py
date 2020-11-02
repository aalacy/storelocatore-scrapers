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
    base_url = "https://www.flywheelsports.com"
    r = session.get("https://www.flywheelsports.com/api/v2/region.json?")
    return_main_object = []
    addresses = []
    state_data = r.json()
    for i in range(len(state_data)):
        state_request = session.get("https://" + str(state_data[i]["region_subdomain"]) + ".flywheelsports.com/api/v2/classroom.json?")
        for store_data in state_request.json():
            store = []
            if store_data["classroom_parent_nid"] != None:
                continue
            store.append("https://www.flywheelsports.com")
            store.append(store_data['classroom_name'])
            if store_data["classroom_address"] in addresses:
                continue
            addresses.append(store_data['classroom_address'])
            if store_data["classroom_structured_address"]['addr_line_1'] == None:
                store_address = store_data["classroom_address"].replace("\n",",")
                if len(store_address.split(",")) < 4 and "New York" in store_address:
                    store.append(store_address.split(",")[0].split("New York")[0])
                    store.append("New York")
                    store.append(store_address.split(",")[-2].strip())
                    store.append(store_address.split(",")[-1])
                elif len(store_address.split(",")[-1]) == 5:
                    store.append(store_address.split(",")[0])
                    store.append(store_address.split(",")[1])
                    store.append(store_address.split(",")[-2].strip())
                    store.append(store_address.split(",")[-1])
                else:
                    store.append(store_address.split(",")[0])
                    store.append(store_address.split(",")[1])
                    store.append(store_address.split(",")[-1].split(" ")[1])
                    store.append(store_address.split(",")[-1].split(" ")[2])
            else:
                store.append(store_data["classroom_structured_address"]['addr_line_1'])
                store.append(store_data["classroom_structured_address"]['city'])
                store.append(store_data["classroom_structured_address"]['state'])
                store.append(store_data["classroom_structured_address"]['zip'])
            store.append("US")
            store.append(store_data["classroom_nid"])
            store.append(store_data["classroom_phone"])
            store.append(store_data["classroom_type"])
            store.append(store_data["classroom_lat"])
            store.append(store_data["classroom_lon"])
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
