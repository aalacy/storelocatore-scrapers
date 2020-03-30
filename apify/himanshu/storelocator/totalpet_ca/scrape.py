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
    base_url = "http://totalpet.ca"
    r = session.get("http://totalpet.ca/store-locator/",headers=headers)
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    hours_object = {}
    phone_object = {}
    for location in soup.find_all("section",{"itemscope":"itemscope"}):
        location_details = list(location.stripped_strings)
        if len(location_details) < 2:
            continue
        for k in range(len(location_details)):
            if "Store Hours" in location_details[k]:
                hours = " ".join(location_details[k+1:])
                hours_object[location_details[0].lower()] = hours
                phone_object[location_details[0].lower()] = location_details[3]
    data_request = session.get("http://totalpet.ca/wp-admin/admin-ajax.php?action=store_search&lat=56.130366&lng=-106.34677099999999&max_results=50&search_radius=1000000&autoload=1",headers=headers)
    data = data_request.json()
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("http://totalpet.ca")
        store.append(store_data["store"])
        store.append(store_data["address"] + store_data["address2"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["zip"])
        store.append("CA")
        store.append(store_data["id"])
        store.append(phone_object[store_data["store"].lower()])
        store.append("total pet")
        store.append(store_data['lat'])
        store.append(store_data['lng'])
        store.append(hours_object[store_data["store"].lower()])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
