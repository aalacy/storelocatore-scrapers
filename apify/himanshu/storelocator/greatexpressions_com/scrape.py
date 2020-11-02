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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.greatexpressions.com"
    r = session.get("https://www.greatexpressions.com/wp-admin/admin-ajax.php?action=fetch_offices_updated_again&page=1&search_type=zip&zip=11756&city=&state=&radius=100000&search=",headers=headers)
    return_main_object = []
    page_size = r.json()['data']["maxPages"]
    for i in range(1,int(page_size) + 1):
        page_request = session.get("https://www.greatexpressions.com/wp-admin/admin-ajax.php?action=fetch_offices_updated_again&page=" + str(i) + "&search_type=zip&zip=11756&city=&state=&radius=100000&search=",headers=headers)
        for store_data in page_request.json()["data"]["posts"]:
            store = []
            store.append("https://www.greatexpressions.com")
            store.append(store_data["service_title"] if store_data["service_title"] else "<MISSING>")
            store.append(store_data["address"] if store_data["address"] else "<MISSING>")
            store.append(store_data["city"] if store_data["city"] else "<MISSING>")
            store.append(store_data["state"] if store_data["state"] else "<MISSING>")
            store.append(store_data["zip_code"] if store_data["zip_code"] else "<MISSING>")
            store.append("US")
            store.append(store_data["ID"])
            store.append(store_data["tel"])
            store.append("great expressions")
            store.append(store_data["lat"])
            store.append(store_data["lng"])
            hours = ""
            for store_hours in store_data["hours"]:
                hours = hours + " " + store_hours["day"] + " " + store_hours["hours"]
            store.append(hours if hours != "" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
