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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    base_url = "https://www.oktire.com"

    ca_provinces_codes = {'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT'}
    final_data = []
    for province in ca_provinces_codes:
        data = {'action': 'api_oktire_stores',
                'path': 'search',
                'filter[radius]': '99999',
                'filter[city]': '',
                'filter[zip]': '',
                'filter[country]': '',
                'filter[loc]': '',
                'filter[province][]': province,
                'summarize': '1',
                'limit': '9999',
                'offset': '0'}

        r = session.post("https://www.oktire.com/wp-admin/admin-ajax.php",headers=headers,data=data)
        return_main_object = []
        location_list = r.json()["items"]
        for i in range(len(location_list)):
            store_data = location_list[i]
            store = []
            store.append("https://www.oktire.com")
            store.append(store_data["name"])
            store.append(store_data["address"]["street"])
            store.append(store_data["address"]["city"])
            store.append(store_data["address"]["province"])
            store.append(store_data["address"]["postal"])
            store.append("CA")
            store.append(store_data["id"])
            store.append(store_data["contact"]["phone"]["formatted"] if store_data["contact"]["phone"]["formatted"] != "" else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["coords"]["lat"])
            store.append(store_data["coords"]["lng"])
            hours = ""
            store_hours = store_data["hours"]
            for key in store_hours:
                hours = hours + " " + store_hours[key]["label"] + " " + store_hours[key]["hours"]
            store.append(hours if hours  != "" else "<MISSING>")
            store.append(store_data["url"])
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            final_data.append(store)
    return final_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
