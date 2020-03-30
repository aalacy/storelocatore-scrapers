# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
# import zulu
import json
import time


session = SgRequests()

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = session.post(url,headers=headers,data=data)
                else:
                    r = session.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None

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
        'Accept': 'application/json, text/plain, */*',

    }

    base_url = "https://www.firstcash.com/king-pawn"
    link = "http://find.cashamerica.us/api/stores?p=1&s=1068&lat=33.5973&lng=-112.1073&d=2020-03-18T12:13:28.997Z&key=D21BFED01A40402BADC9B931165432CD"
    r = request_wrapper(link,'get',headers=headers)
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
        location_type = location['brand']
        store_number =  str(location['storeNumber'])
        http = "http://find.cashamerica.us/api/stores/"+str(store_number)+"?key=D21BFED01A40402BADC9B931165432CD"
        page_url =http
        all_data = request_wrapper(http,'get', headers=headers).json()
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
