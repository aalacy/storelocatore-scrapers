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
    base_url = "https://www.bigmsupermarkets.com"
    r = session.get("https://www.bigmsupermarkets.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all('script'):
        if "var stores =" in script.text:
            location_list = json.loads(script.text.split("var stores = ")[1].split("}];")[0] + "}]")
            for i in range(len(location_list)):
                store_data = location_list[i]
                store = []
                store.append("https://www.bigmsupermarkets.com")
                store.append(store_data["name"])
                store.append(store_data["address1"])
                store.append(store_data["city"])
                store.append(store_data["state"])
                store.append(store_data["zipCode"])
                store.append("US")
                store.append(store_data["storeID"])
                store.append(store_data["phone"] if store_data["phone"]  != "" else "<MISSING>")
                store.append("big m supermarkets")
                store.append(store_data["latitude"])
                store.append(store_data["longitude"])
                store.append(BeautifulSoup(store_data["hourInfo"],"lxml").get_text().replace("\n"," ") if  "hourInfo" in store_data and store_data["hourInfo"] != ""  else "<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

