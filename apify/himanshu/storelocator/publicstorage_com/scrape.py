import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 30
    zip_code = search.next_zip()
    current_results_len = 0
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            "content-type": "application/json;charset=UTF-8",
            "Accept": "application/json, text/plain, */*"
        }
    base_url = "https://www.publicstorage.com"
    while zip_code:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s...' % (str(zip)))
        data = '{"location":"' + str(zip_code) + '"}'
        
        r = requests.post("https://www.publicstorage.com/api/sitecore/LocationSearch/RedoSearch",headers=headers,data=data).json()
        current_results_len = len(r["Result"]["Units"])
        for i in r["Result"]["Units"]:
            street_address = i['Street1']
            city = i['City']
            state = i['StateCode']
            zipp = i['PostalCode']
            store_number = i['SiteID']
            phone = i['PhoneNumber']
            latitude = i['Latitude']
            longitude = i['Longitude']
            page_url = base_url + i['PLPUrl']
            try:
                r1 = requests.get(page_url, headers=headers)
            except:
                continue
            soup1 = BeautifulSoup(r1.text, "lxml")
            location_name = soup1.find("h1",{"class":"ps-properties-property-header__header"}).text

            hours_of_operation = str(''.join(list(soup1.find_all("div",{"class":'ps-properties-property__info__hours__section'})[0].text))) + " " + str(''.join(list(soup1.find_all("div",{"class":'ps-properties-property__info__hours__section'})[1].text)))
        
            result_coords.append((latitude, longitude))
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number) 
            store.append(phone if "PhoneNumber" in i and i["PhoneNumber"] else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation if hours_of_operation != "" else "<MISSING>")
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # print(store)
            yield store


        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
