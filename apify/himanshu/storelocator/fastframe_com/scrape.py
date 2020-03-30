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
    base_url = "https://fastframe.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    r = session.get(base_url + "/wp-admin/admin-ajax.php?action=asl_load_stores&load_all=1&layout=1",headers=headers)
    data = r.json()
    return_main_object = []
    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://fastframe.com")
        store.append(store_data['title'])
        store.append(store_data["street"])
        store.append(store_data['city'])
        store.append(store_data['state'])
        if store[-1] == "BH":
            continue
        store.append(store_data["postal_code"])
        store.append("US")
        store.append(store_data["id"])
        store.append(store_data["phone"])
        store.append("fast frame")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        hours = ""
        open_hours = json.loads(store_data["open_hours"])
        for key in open_hours:
            if open_hours[key] == "0":
                continue
            else:
                hours = hours + " " + key + " " +  open_hours[key][0] + " "
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
