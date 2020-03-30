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
    base_url = "https://bellstores.com"
    r = session.get(base_url + "/home/locations")
    soup = BeautifulSoup(r.text,"lxml")
    scripts = soup.find_all("script")
    return_main_object = []
    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if "var locations" in script.text:
            location_list = json.loads(script.text.split("var locations = ")[1].split("]")[0] + "]")
            for i in range(len(location_list)):
                store_data = location_list[i]
                store = []
                store.append("https://bellstores.com")
                store.append(store_data['Name'])
                store.append(store_data["Address1"])
                store.append(store_data['City'])
                store.append(store_data['State'])
                store.append(store_data["Zip"])
                store.append("US")
                store.append(store_data['StoreNumber'])
                store.append(store_data['PhoneNumber'])
                store.append("bell stores")
                store.append(store_data["Latitude"])
                store.append(store_data["Longitude"])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
