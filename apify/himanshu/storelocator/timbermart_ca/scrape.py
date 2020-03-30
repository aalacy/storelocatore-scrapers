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
    base_url = "https://timbermart.ca"
    r = session.get("https://timbermart.ca/wp-json/timberfeed/v1/stores",headers=headers)
    data = r.json()["data"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://timbermart.ca")
        store.append(store_data["name"])
        store.append(store_data["address"]["street"])
        store.append(store_data["address"]["city"])
        store.append(store_data["address"]["province"])
        store.append(store_data["address"]["postal_code"])
        store.append("CA")
        store.append(store_data["id"])
        store.append(store_data["contact"]["phone"])
        store.append("hancocks timber mart")
        store.append(store_data["location"]["lat"])
        store.append(store_data["location"]["lng"])
        store.append("today's hours " + store_data["today"] if store_data["today"] != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
