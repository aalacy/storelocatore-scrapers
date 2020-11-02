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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.tacopalenque.com"
    r = session.get("https://www.tacopalenque.com/wp-content/themes/tacoPalenque2017/includes/jquery-store-locator-plugin/data/locations.xml?formattedAddress=&boundsNorthEast=&boundsSouthWest=",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    i = 1
    for store_data in soup.find_all("marker"):
        store = []
        store.append("https://www.tacopalenque.com")
        store.append(store_data["name"])
        store.append(store_data["address"] + " " + store_data["address2"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["postal"])
        store.append(store_data["country"])
        store.append(i)
        store.append(store_data["phone"].split("/")[0] if store_data["phone"] != "" and store_data["phone"] != "Coming Soon" and store_data["phone"] != "TBD" else "<MISSING>")
        i = i + 1
        store.append("taco palenque")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append((store_data["hours1"] + " " + store_data["hours2"] + " " + store_data["hours3"]).replace("–","-"))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
