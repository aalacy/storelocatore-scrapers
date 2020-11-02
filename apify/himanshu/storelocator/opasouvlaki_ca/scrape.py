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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://opasouvlaki.ca"
    r = session.get("https://opasouvlaki.ca/wp-json/opasouvlaki/v1/search-locations/11756",headers=headers)
    data = r.json()
    return_main_object = []
    for store_data in data:
        store = []
        store.append("https://opasouvlaki.ca")
        store.append(store_data['location'])
        store.append(store_data["shortaddress"])
        store.append(store_data['city'])
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("US" if int(store_data["latitude"].split(".")[0]) < 39 else "CA")
        store.append(store_data["id"])
        store.append(store_data["phone"])
        store.append("opa of greece")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        hours = ""
        hours = hours + " monday " + store_data["monday"]["open"] + " - " + store_data["monday"]["close"]
        hours = hours + " tuesday " + store_data["tuesday"]["open"] + " - " + store_data["tuesday"]["close"]
        hours = hours + " wednesday " + store_data["wednesday"]["open"] + " - " + store_data["wednesday"]["close"]
        hours = hours + " thursday " + store_data["thursday"]["open"] + " - " + store_data["thursday"]["close"]
        hours = hours + " friday " + store_data["friday"]["open"] + " - " + store_data["friday"]["close"]
        hours = hours + " saturday " + store_data["saturday"]["open"] + " - " + store_data["saturday"]["close"]
        hours = hours + " sunday " + store_data["sunday"]["open"] + " - " + store_data["sunday"]["close"]
        store.append(hours if hours != "" else "<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
