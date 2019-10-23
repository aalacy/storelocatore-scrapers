import csv
import requests
import json
import sgzip
from bs4 import BeautifulSoup
import time
from random import randrange
import re

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.zipscarwash.com"
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 8
    coord = search.next_coord()
    while coord:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        x = coord[0]
        y = coord[1]
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        r = requests.get("https://www.zipscarwash.com/locations?field_map_proximity-lat=" + str(x) + "&field_map_proximity-lng=" + str(y) + "&field_map_proximity=1500000",headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        for location in soup.find_all("div",{"class":"views-col"}):
            geo_location = location.find("a",text="Directions")["href"]
            lat = geo_location.split("lat=")[1].split("&")[0]
            lng = geo_location.split("long=")[1].split("&")[0]
            result_coords.append((lat, lng))
            store = []
            name = " ".join(list(location.find("div",{"class":"views-field-title"}).stripped_strings))
            address = " ".join(list(location.find("span",{"class":"address-line1"}).stripped_strings))
            city = " ".join(list(location.find("span",{"class":"locality"}).stripped_strings))
            state = " ".join(list(location.find("span",{"class":"administrative-area"}).stripped_strings))
            store_zip = " ".join(list(location.find("span",{"class":"postal-code"}).stripped_strings))
            page_url = base_url + location.find("a")["href"]
            if location.find("a",{"href":re.compile("tel:")}):
                phone = location.find("a",{"href":re.compile("tel:")}).text
            else:
                phone = "<MISSING>"
            store = []
            store.append("https://www.zipscarwash.com")
            store.append(name)
            store.append(address)
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(city)
            store.append(state)
            store.append(store_zip if store_zip else "<MISSING>")
            store.append("US")
            store.append(page_url.split("/")[-1])
            store.append(phone)
            store.append("<MISSING>")
            store.append(geo_location.split("lat=")[1].split("&")[0])
            store.append(geo_location.split("long=")[1].split("&")[0])
            location_request = requests.get(page_url,headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            hours = " ".join(list(location_soup.find("div",{"class":"office-hours"}).stripped_strings))
            store.append(hours.replace("  ","") if hours else "<MISSING>")
            store.append(page_url)
            # print(store)
            yield store
        if len(soup.find_all("div",{"class":"views-col"})) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
