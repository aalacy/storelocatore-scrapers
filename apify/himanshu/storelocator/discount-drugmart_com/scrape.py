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
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    r = session.get("https://discount-drugmart.com/our-store/store-locator/#o=0&t=&ot=oc1&oc=1000&m=10000&s=11756",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    for script in soup.find_all("script"):
        if "var stores = " in script.text:
            location_list = json.loads(script.text.split("var stores = ")[1].split("];")[0] + "]")
            for store_data in location_list:
                store = []
                store.append("https://discount-drugmart.com")
                store.append("Discount Drug Mart #" + str(store_data["store"]))
                store.append(store_data["address"])
                store.append(store_data["city"])
                store.append(store_data["state"])
                store.append(store_data["zip"])
                store.append("US")
                store.append(store_data["store"])
                store.append(store_data["phone"] if store_data["phone"] else "<MISSING>")
                store.append("<MISSING>")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                hours = ""
                for key in store_data:
                    if "_hours" in key:
                        if store_data[key] == "":
                            hours = hours + " " + key.split("_")[0] + " N/A"
                        else:
                            hours = hours + " " + key.split("_")[0] + " " + store_data[key]
                store.append(hours if hours else "<MISSING>")
                yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()