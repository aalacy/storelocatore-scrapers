import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import ast

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
    base_url = "https://www.shopassociated.com"
    r = session.get(base_url + "/locations/?addr=")
    soup = BeautifulSoup(r.text,"lxml")
    scripts = soup.find_all("script")
    return_main_object = []
    for script in scripts:
        if "var locations" in script.text:
            location_list = ast.literal_eval(script.text.split("var locations = ")[1].split("]")[0] + "]")
            for i in range(len(location_list)):
                store_object = location_list[i]
                store = []
                store.append("https://www.shopassociated.com")
                store.append(store_object["name"])
                store.append(store_object["address1"])
                store.append(store_object["city"] if store_object["city"] != "" else "<MISSING>")
                store.append(store_object["state"] if store_object["state"] != "" else "<MISSING>")
                store.append(store_object["zipCode"] if store_object["zipCode"] != "" else "<MISSING>")
                store.append("US")
                store.append(store_object["storeNumber"] if store_object["storeNumber"] != "" else "<MISSING>")
                store.append(store_object["phone"] if store_object["phone"] != "" else "<MISSING>")
                store.append("Associated supermarket group")
                store.append(store_object["latitude"] if store_object["latitude"] != "" else "<MISSING>")
                store.append(store_object["longitude"] if store_object["longitude"] != "" else "<MISSING>")
                if "hourInfo" in store_object:
                    store.append(store_object["hourInfo"] if store_object["hourInfo"] != "" else "<MISSING>")
                else:
                    store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
