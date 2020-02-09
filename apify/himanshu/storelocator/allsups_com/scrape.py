import csv
import sys

import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Accept':'application/json, text/javascript, */*; q=0.01'}
    return_main_object = []
    base_url = "https://www.dunkindonuts.com/"
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["US", "CA"])
    postcode = search.next_zip()

    MAX_RESULTS = 10000
    # MAX_COUNT = 32
    MAX_DISTANCE = 100
    coord = search.next_coord()
    current_results_len =0
    addresses = []
   

    while coord:
        result_coords = []
        x = coord[0]
        y = coord[1]
        addresses =[]
        z = str(search.current_zip)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": "https://allsups.com/locations",
            "Host": "allsups.com",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": "19",
            # "csrf-token":"undefined",
            # "origin": "https://www.dunkindonuts.com",
            # "referer": "https://www.dunkindonuts.com/en/locations?location="+str(z),

        }
        
        data = "radius=25&zip="+str(z)
        # print(z)
        # try:
        locator_domain = "https://allsups.com"
        try:
            json_data = requests.post("https://allsups.com/ajax/Search.ashx",data=data,headers=headers).json()
        except:
            pass
        # print(json_data)
        for data in json_data:
            street_address=''
            city =''
            state =''
            latitude =''
            longitude =''
            store_number =''
            location_name =''
            country_code = ''
            phone =''
            location_type=''
            zip=''
            hours=''
            page_url=''
            if "address" in  data:
                street_address = data['address'].strip()
            if "city" in data:
                city =data['city'].strip()
            if "state" in data:
                state =data['state'].strip()
            if  "latitude" in data:
                latitude = data['latitude']
                longitude = data['longitude']
            if "id" in data:
                store_number =data['id']
            if "title" in data:
                location_name = data['title'].strip()

            if "zip" in data:
                zip = data['zip']
            hours = '<MISSING>'
            store = []

            # print("~~~~~~~~~~~~~~~~ ",street_address)
            if "address" in  data:
                street_address = data['address'].strip()
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
                result_coords.append((latitude, longitude))
                store.append(
                    hours if hours else '<MISSING>')
                store.append(page_url if page_url else "<MISSING>")
                if street_address in addresses:
                    continue
                addresses.append(street_address)
                if "<MISSING>" in store[3]:
                    pass
                else:
                    yield store
                # print()
                # print("data == " + str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                
        # except:
        #     pass
        
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")

        coord = search.next_coord()
       
    # return return_main_object


def scrape():
    data = fetch_data()

    write_output(data)


scrape()
