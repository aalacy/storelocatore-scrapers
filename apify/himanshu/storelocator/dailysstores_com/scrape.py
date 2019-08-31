import csv
import requests
from bs4 import BeautifulSoup
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://dailysstores.com/_pages/locations_json"
    r = requests.get(base_url).json()
    return_main_object = []
    for i in range(len(r)):
        store = []
        store.append("http://dailysstores.com")
        store.append(r[i]['title'].replace("&#8217;","'"))
        store.append(r[i]['street_address'])
        store.append(r[i]['city_name'])
        store.append(r[i]['state'])
        if r[i]['zip_code']!="":
            store.append(r[i]['zip_code'].strip())
        else:
            store.append("<MISSING>")
        store.append("US")
        store.append(r[i]['id'])
        store.append(r[i]['phone_number'])
        store.append('dailysstores')
        if r[i]['latitude']:
            store.append(r[i]['latitude'])
        else:
            store.append("<MISSING>")
        if r[i]['longitude']:
                store.append(r[i]['longitude'])
        else:
            store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
