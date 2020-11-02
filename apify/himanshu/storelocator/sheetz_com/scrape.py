# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://sheetz.com/"

    location_url ="https://orderz.sheetz.com/sas/store?fuelPrice=true"
        
    r = session.get(location_url, headers=headers)
    json_data = r.json()
    for i in json_data:
        store_number = i['storeNumber']
        street_address = i['address']
        city = i['city']
        state = i['state']
        zipp = i['zip'][0:5]
        if "phone" in i:
            phone = i['phone']  
        latitude = i['latitude']
        longitude = i['longitude']
        page_url = "https://orderz.sheetz.com/#/main/location/store/"+str(store_number)
       
        store = []
        store.append(base_url)
        store.append("<MISSING>")
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append(store_number) 
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append("open 24/7")
        store.append(page_url)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
