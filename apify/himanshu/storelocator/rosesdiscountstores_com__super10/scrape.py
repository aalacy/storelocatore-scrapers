# coding=UTF-8
import csv
import requests
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
import json
session = SgRequests()

def write_output(data):
    with open('data.csv',newline="", mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    base_url = "https://www.rosesdiscountstores.com/#super10"
    link = "https://api.zenlocator.com/v1/apps/app_vfde3mfb/locations/search?countryCode=US&name=Super%2010&query=Super%2010&radius=700000"
    json_data = requests.get(link, headers=headers).json()['locations']
    for data in json_data:
        location_name = data['name']
        street_address = data['address1']
        city = data['city']
        state = data['region']
        zipp = data['postcode']
        country_code = data['countryCode']
        phone = data['contacts']['con_wg5rd22k']['text']
        latitude = data['lat']
        longitude = data['lng']
        hours_of_operation = ""
        if type(data["hours"]) == dict:
            for key in data["hours"]["hoursOfOperation"]:
                hours_of_operation = hours_of_operation + key + " " +data["hours"]["hoursOfOperation"][key].replace("-"," to ") + " "
        elif data["hours"] == "hrs_a4db656x":
            hours_of_operation = "mon 9 am to 6 pm tue 9 am to 6 pm wed 9 am to 6 pm thurs 9 am to 6 pm fri 9 am sat 6 am to 9pm sun 12 am to 6 pm"
        else:
            hours_of_operation = data["hours"]
        store = []
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code)
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append("Super 10")
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append("<MISSING>")
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
