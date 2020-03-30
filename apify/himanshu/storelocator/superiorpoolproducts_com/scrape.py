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
    base_url = "http://superiorpoolproducts.com"
    r = session.get("http://superiorpoolproducts.com/map_api/map.php",headers=headers)
    data = json.loads(r.text.split("var LocsAB =")[1].split("}];")[0]+"}]")
    return_main_object = []
    geo_locations = []
    for i in range(len(data)):
        zip_code = data[i]["html"].split(" ")[-1]
        zip_request = session.get("http://superiorpoolproducts.com/map_api/?z=" + str(zip_code),headers=headers)
        zip_data = zip_request.json()["locations"]
        for k in range(len(zip_data)):
            store_data = zip_data[k]
            if store_data["latlon"] in geo_locations:
                continue
            geo_locations.append(store_data["latlon"])
            store = []
            store.append("http://superiorpoolproducts.com")
            store.append(store_data["sitename"])
            store.append(store_data["address1"] + store_data["address2"] if "address2" in store_data else store_data["address1"])
            store.append(store_data["city"])
            store.append(store_data["state"])
            store.append(store_data["zip"])
            store.append("US")
            store.append("<MISSING>")
            store.append(store_data["phone"])
            store.append("superior pool products")
            store.append(store_data["latlon"].split(",")[0])
            store.append(store_data["latlon"].split(",")[1])
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
