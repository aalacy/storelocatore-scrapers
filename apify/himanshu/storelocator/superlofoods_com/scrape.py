import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import ast
import unicodedata


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding='utf8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }

    base_url = "http://superlofoods.com"
    r = session.get("https://api.freshop.com/1/stores?app_key=superlo", headers=headers)
    data = r.json()['items']

    for store_data in data:
        store = []
        location_name = store_data['name']
        if('address_1'in store_data):
            street_address = store_data['address_1']
            city = store_data['city']
            state = store_data['state']
            zipp = store_data['postal_code']
            phone = store_data['phone_md'].split("\nFax")[0]
            latitude = store_data['latitude']
            longitude = store_data['longitude']
            hour = store_data['hours_md']
            store_id = store_data['id']
            if location_name in addresses:
                continue
            addresses.append(location_name)
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_id)
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hour)
            store.append(store_data["url"])
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
