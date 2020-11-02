import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    base_url = "https://www.loewshotels.com"
    r = session.get("https://www.loewshotels.com/destinations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for script in soup.find_all("script"):
        if "var propertiesPinJSON = " in script.text:
            location_list = json.loads(script.text.split("var propertiesPinJSON = ")[1].split("}}}")[0] + "}}}")["points"]
            for key in location_list:
                store_data = location_list[key]
                store = []
                store.append("https://www.loewshotels.com")
                store.append(store_data["name"])
                store.append(store_data["address"])
                store.append(store_data["city"])
                store.append(store_data["state"])
                store.append(store_data["zip"] if len(store_data["zip"]) != 6 else store_data["zip"][:3] + " " + store_data["zip"][3:])
                store.append("US" if len(store_data["zip"]) == 5 else "CA")
                store.append(store_data["id"])
                store.append(store_data["phone"] if store_data["phone"] != "" else "<MISSING>")
                store.append("loews hotels")
                store.append(store_data["lat"])
                store.append(store_data["lng"])
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
