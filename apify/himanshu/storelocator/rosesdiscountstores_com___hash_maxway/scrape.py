# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
from sgrequests import SgRequests
session = SgRequests()
import json


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
    addresses = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',

    }

    base_url = "https://www.rosesdiscountstores.com/"
    link = "https://api.zenlocator.com/v1/apps/app_vfde3mfb/init?widget=MAP"
    json_data = requests.get(link, headers=headers).json()['locations']
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = "Maxway"
    latitude = ""
    longitude = ""
    hours = ""
    page_url = "https://www.rosesdiscountstores.com/store-locator-index"
    for data in json_data:
        location_name = data['name']
        if "Maxway" not in location_name:
            continue
        addr = data['address'].split(",")
        if " US" == addr[-1]:
            del addr[-1]
        if "United States" in addr[-1]:
            del addr[-1]
        if data['address1']:
            street_address = (data['address1']+ " " + str(data['address2'])).strip()
        else:
            street_address = " ".join(addr[:-2]).strip()
        if data['city']:

            city = data['city']
        else:
            city = addr[1].strip()
        state = data['region']
        if data['postcode']:
            zipp = data['postcode']
        else:
            try:
                zipp = re.findall(r'\b[0-9]{5}(?:-[0-9]{4})?\b',data['address'])[-1].strip()
            except:
                zipp = "<MISSING>"
        if "con_wg5rd22k" in data['contacts']:
            phone = data['contacts']['con_wg5rd22k']['text']
        else:
            phone = "<MISSING>"
        latitude = data['lat']
        longitude = data['lng']
        hours = "Monday 9am-9pm Tuesday 9am-9pm Wednesday 9am-9pm Thursday 9am-9pm Friday 9am-9pm Saturday 9am-9pm Sunday 10am-8pm"

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    store_number, phone, location_type, str(latitude), str(longitude), hours,page_url]

        # if str(store[2]) + str(store[-3]) not in addresses:
        #     addresses.append(str(store[2]) + str(store[-3]))

        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store

        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
