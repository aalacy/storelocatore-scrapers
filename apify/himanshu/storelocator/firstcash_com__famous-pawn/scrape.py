# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    }

    base_url = "https://www.firstcash.com/famous-pawn"
    link = "http://find.cashamerica.us/api/stores?p=1&s=1068&lat=32.72&lng=-97.45&d=2019-11-11T13:33:27.150Z&key=D21BFED01A40402BADC9B931165432CD"
    r = requests.get(link, headers=headers)
    json_data = r.json()
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    for location in json_data:
        store_number =  str(location['storeNumber'])
        http = "http://find.cashamerica.us/api/stores/"+str(store_number)+"?key=D21BFED01A40402BADC9B931165432CD"
        page_url =http
        try:
            all_data = requests.get(http, headers=headers).json()
        except:
            continue
        location_name = location['brand']
        street_address = all_data['address']['address1']
        city = all_data['address']['city']
        state = all_data['address']['state']
        zipp = all_data['address']['zipCode']
        latitude = str(location['latitude'])
        longitude = str(location['longitude'])
        phone = all_data['phone']
        hours_of_operation1 ='' 
        if "weeklyHours" in all_data:
            hours_of_operation = all_data['weeklyHours']
            for i in hours_of_operation:
                hours_of_operation1 = hours_of_operation1 +' ' +(i['weekDay'] + ' ' + i['openTime'] + ' ' +i['closeTime'])
        else:
            hours_of_operation = '<MISSING>' 
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                    str(store_number), str(phone), location_type, str(latitude), str(longitude), hours_of_operation1,page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
