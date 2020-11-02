import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    cords = sgzip.coords_for_radius(200)
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "X-Requested-With": "XMLHttpRequest",
        "Accept": "application/json, text/plain, */*",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    for cord in cords:
        base_url = "https://lemontree.com"
        data = "action=get_stores&lat=" + str(cord[0]) + "&lng=" + str(cord[1]) + "&radius=200&categories%5B0%5D="
        r = session.post("https://lemontree.com/wp-admin/admin-ajax.php",headers=headers,data=data)
        r_data = r.json()
        for key in r_data:
            store_data = r_data[key]
            store = []
            store.append("https://lemontree.com")
            store.append(store_data["na"])
            store.append(store_data["st"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["ct"])
            store.append(store_data["rg"])
            store.append(store_data["zp"])
            store.append("<MISSING>")
            store.append(store_data["ID"])
            store.append(store_data["te"] if store_data["te"] != "" and store_data["te"] != None else "<MISSING>")
            store.append("lemon tree family salons")
            store.append(store_data["lat"])
            store.append(store_data["lng"])
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
