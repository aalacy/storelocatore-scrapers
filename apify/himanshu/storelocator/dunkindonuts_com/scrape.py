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
    search.initialize(country_codes = ["us", "ca"])
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
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "csrf-token":"undefined",
            "origin": "https://www.dunkindonuts.com",
            "referer": "https://www.dunkindonuts.com/en/locations?location="+str(z),

        }
      
        data = "service=DSL&origin="+str(x)+"%2C"+str(y)+"&radius=500&maxMatches=500"
        try:
            json_data = requests.post("https://www.dunkindonuts.com/bin/servlet/dsl",data=data,headers=headers).json()
        except:
            pass
        if "storeAttributes" in json_data['data']:
            for data in json_data['data']['storeAttributes']: 
                store_number = '<MISSING>'
                page_url = '<MISSING>'
                locator_domain = base_url
                street_address = data['address'].strip()
                city = data['city'].strip()
                state = data['state'].strip()
                zip = data['postal'].strip()
                country_code = data['country']
                location_name = data['name']
                latitude = data['lat']
                location_type ='<MISSING>'
                longitude = data['lng']
                hours = " mon "+ data['mon_hours'] + ' tue ' +  data['tue_hours'] + ' wed ' + data['wed_hours'] + ' thu ' + data['thu_hours'] + ' fri '+ data['fri_hours'] + ' sun ' + data['sun_hours']
                # phone = data['phonenumber']
                if data['phonenumber'] == '--':
                    phone = '<MISSING>'
                else:
                    phone = data['phonenumber'].strip()

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
                result_coords.append((latitude, longitude))
                store.append(
                    hours.strip() if hours.strip() else '<MISSING>')
                store.append(page_url if page_url else "<MISSING>")
                if street_address in addresses:
                    continue
                addresses.append(street_address)
                # print()
                #print("data == " + str(store))
               # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store


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
