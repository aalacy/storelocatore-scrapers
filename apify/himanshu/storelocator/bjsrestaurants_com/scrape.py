# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import urllib.request

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 30
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Host": "www.bjsrestaurants.com",
        "Referer":"https://www.bjsrestaurants.com/locations",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36",
    }

    base_url = "https://www.bjsrestaurants.com"

    while coord:
        result_coords = []
        lat = str(coord[0])
        lng = str(coord[1])
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        
        location_url = "https://www.bjsrestaurants.com/locations?searchString="+str(search.current_zip)+"&lat="+lat+"&lng="+lng+"#first"
        # print(location_url)
        try:
            r = requests.get(location_url, headers=headers)
        except:
            continue
        soup_loc = BeautifulSoup(r.text, "lxml")
        
        tag_store = soup_loc.find_all("a",{"class":"btn ghost secondary"})
        # print(tag_store)
        
        current_results_len = len(tag_store)
        for tage in tag_store:
            # print(tage['href'])
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
            raw_address = ""
            hours_of_operation = ""

          
            r1 = requests.get("https://www.bjsrestaurants.com"+tage['href'], headers=headers)
            soup_loc1 = BeautifulSoup(r1.text, "lxml")
            street_address = list(soup_loc1.find("p",{"class":"address"}).stripped_strings)[0]
            city =list(soup_loc1.find("p",{"class":"address"}).stripped_strings)[1].split(",")[0]
            str_data = list(soup_loc1.find("p",{"class":"address"}).stripped_strings)[1].split(",")[1]
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(str_data))
            state_list = re.findall(r' ([A-Z]{2})', str(str_data))
            # print(soup_loc1.find("div",{"data-map-type":"location-detail"})['data-lat'])

            try:
                phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(soup_loc1.find("div",{"class":"phone-and-directions"}).text))
            except:
                phone_list =''

            try:
                hours_of_operation = " ".join(list(soup_loc1.find("div",{"class":"location__hours"}).stripped_strings)).split("Special Hours")[0].split('Restaurant Hours')[1].strip()
               
            except:
                hours_of_operation =''

            try:
                latitude = soup_loc1.find("div",{"data-map-type":"location-detail"})['data-lat']
                longitude = soup_loc1.find("div",{"data-map-type":"location-detail"})['data-lng']
            except:
                latitude =''
                longitude =''



            page_url = "https://www.bjsrestaurants.com"+tage['href']

            try:
                location_name = soup_loc1.find("h1",{"class":"m0"}).text.strip()
            except:
                location_name =''


            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"
        
            if phone_list:
                phone =  phone_list[-1]

            if state_list:
                state = state_list[-1]

            # print("location ==== " + str(location))
            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
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
        # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
