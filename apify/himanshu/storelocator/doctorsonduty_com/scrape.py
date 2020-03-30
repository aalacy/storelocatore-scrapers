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
    base_url = "http://doctorsonduty.com"
    r = session.get("https://www.clockwisemd.com/groups/84")
    soup = BeautifulSoup(r.text,"lxml")
    scripts = soup.find_all("script")
    return_main_object = []
    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if "var hsp_info" in script.text:
            location_list = json.loads(script.text.split("var hsp_info = ")[1].split("];")[0] + "]")
            for i in range(len(location_list)):
                store_data = location_list[i]
                store = []
                store.append("http://doctorsonduty.com")
                store.append(store_data['hospital_name'])
                store.append(store_data["address_1"])
                store.append(store_data['city'])
                store.append(store_data['state'])
                store.append(store_data["zip"])
                store.append("US")
                store.append(store_data['hospital_id'])
                store.append(store_data['phone_number'])
                store.append("doctors on duty")
                store.append(store_data["coords"][0])
                store.append(store_data["coords"][1])
                store.append("<INACCESSIBLE>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
