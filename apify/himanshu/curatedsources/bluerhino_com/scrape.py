import csv
import requests
from bs4 import BeautifulSoup
import re
import json
# import sgzip


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # zips = sgzip.for_radius(100)
    addresses = []
    return_main_object = []
    header = {
        'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    base_url = "https://bluerhino.com/"

    loacation_url = 'https://bluerhino.com/api/propane/GetRetailersNearPoint?latitude=40.8&longitude=-73.65&radius=10000&name=&type=&top=3000000&cache=false'
    r = requests.get(loacation_url, headers=header).json()
    locator_domain = base_url
    for id, vj in enumerate(r):

        locator_domain = base_url

        location_name = vj['RetailName']
        street_address = vj['Address1'].replace('<', '').replace('>', '')
        city = vj['City']
        state = vj['State']
        zip = vj['Zip']
        store_number = vj['StoreNumber']
        country_code = vj['Country']
        phone = vj['Phone']
        location_type = '<MISSING>'
        latitude = vj['Latitude']
        longitude = vj['Longitude']
        hours_of_operation = vj['Hours']
        if street_address in addresses:
            continue

        addresses.append(street_address)

        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')

        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append('<MISSING>')

        return_main_object.append(store)
        #print('===' + str(store))
        #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
