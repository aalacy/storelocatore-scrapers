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
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    data = "action=location_search&search=all&filter="
    base_url = "https://parksterlingbank.com"
    r = session.post("https://www.southstatebank.com/internet/wp-admin/admin-ajax.php",headers=headers,data=data)
    data = r.json()["branches"]
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://parksterlingbank.com")
        store.append(BeautifulSoup(store_data["post_title"],"lxml").get_text())
        if store_data["street"] == None:
            continue
        store.append(BeautifulSoup(store_data["street"],"lxml").text.strip())
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data["ID"])
        store.append(store_data["local_phone"])
        store.append("south state bank")
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        store.append(BeautifulSoup(store_data["lobby_hours_html"],"lxml").get_text())
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
