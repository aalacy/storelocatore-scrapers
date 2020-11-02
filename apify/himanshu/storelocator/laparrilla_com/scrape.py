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
    base_url = "https://laparrilla.com"
    r = session.get("https://laparrilla.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    hours = " ".join(list(soup.find_all("em")[-1].stripped_strings))
    return_main_object = []
    for script in soup.find_all("script"):
        if "var LPAD_SL = " in script.text:
            location_list = json.loads(script.text.split("var LPAD_SL = ")[1].split("};")[0] + "}")["locations"]
            for store_data in location_list:
                store = []
                store.append("https://laparrilla.com")
                store.append(store_data["name"])
                store.append(store_data["_street_1"] + " " + store_data["_street_2"])
                store.append(store_data["_city"])
                store.append(store_data["_state"])
                store.append(store_data["_postal_code"])
                store.append("US")
                store.append("<MISSING>")
                store.append(store_data["_phone"].replace("\u2013",""))
                store.append("the laparrilla")
                store.append(store_data["_latitude"])
                store.append(store_data["_longitude"])
                store.append(hours)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
