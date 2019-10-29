import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast


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
    r = requests.get("https://api.freshop.com/1/stores?app_key=superlo", headers=headers)
    data = r.json()['items']

    for store_data in data:
        return_object = []
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
            return_object.append(base_url)
            return_object.append(location_name)
            return_object.append(street_address)
            return_object.append(city)
            return_object.append(state)
            return_object.append(zipp)
            return_object.append("US")
            return_object.append(store_id)
            return_object.append(phone)
            return_object.append("<MISSING>")
            return_object.append(latitude)
            return_object.append(longitude)
            return_object.append(hour)
            return_object.append("<MISSING>")
            return_main_object.append(return_object)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
