# -*- coding: utf-8 -*-
import csv
import requests
from bs4 import BeautifulSoup
import re
import json,urllib
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://www.wagner-oil.com/store-locator/"
    r = requests.get(base_url)
    soup = BeautifulSoup(r.content,"lxml")
    store_name = []
    store_detail = []
    return_main_object = []
    k = (soup.find('table'))
    for i in k.find_all('tr'):
        data=(list(i.stripped_strings))
        if len(data)==4:
            temp_ver = []
            street_address = data[2]
            city = data[0]
            name = data[1]
            store_name.append(name)
            phone = data[3]
            temp_ver.append(street_address)
            temp_ver.append(city)
            temp_ver.append("<MISSING>")
            temp_ver.append("<MISSING>")
            temp_ver.append("US")
            temp_ver.append("<MISSING>")
            temp_ver.append(phone)
            temp_ver.append("wagner-oil")
            temp_ver.append("<MISSING>")
            temp_ver.append("<MISSING>")
            temp_ver.append("<MISSING>")
            store_detail.append(temp_ver)

    for i in range(len(store_name)):
        store = list()
        store.append("http://www.wagner-oil.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)

  
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
