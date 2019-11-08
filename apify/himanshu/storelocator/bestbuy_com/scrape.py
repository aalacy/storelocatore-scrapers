import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
import unicodedata

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url,headers=headers)
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
                    r = requests.post(url,headers=headers,data=data)
                else:
                    r = requests.post(url,headers=headers)
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

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 20
    # MAX_DISTANCE = 15
    zip = search.next_zip()
    while zip:
        result_coords = []
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s...' % (str(zip)))
        # print("https://www.bestbuy.com/browse-api/2.0/store-locator/" + str(zip))
        r = request_wrapper("https://www.bestbuy.com/browse-api/2.0/store-locator/" + str(zip),"get",headers=headers)
        if r == None:
            # print("failed to pull" + str("https://www.bestbuy.com/browse-api/2.0/store-locator/" + str(zip)))
            continue
        data = r.json()["data"]["stores"]
        for store_data in data:
            if store_data["country"] not in ["CA","US"]:
                continue
            if store_data["hours"] == []:
                continue
            lat = store_data["latitude"]
            lng = store_data["longitude"]
            result_coords.append((lat, lng))
            store = []
            store.append("https://www.bestbuy.com")
            url = "http://stores.bestbuy.com/" + str(store_data["id"])
            # print(url)
            if store_data["locationType"] != "Store":
                if store_data["locationType"] != "Warehouse":
                    pass
                    # print("new type =================" + str(store_data["locationType"]))
                continue
            location_request = request_wrapper(url,"get",headers=headers)
            if location_request == None:
                # print("failed to pull" + str(url))
                continue
            location_soup = BeautifulSoup(location_request.text,"lxml")
            if location_soup.find("span",{"class":'LocationName-geo'}):
                name = location_soup.find("span",{"class":'LocationName-geo'}).text.strip()
            else:
                name = location_soup.find("span",{"id":'location-name'}).text.strip()
            store.append(name)
            store.append(store_data["addr1"] + " " + store_data["addr2"] if "addr2" in store_data else store_data["addr1"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["city"]  if store_data["city"] else "<MISSING>")
            store.append(store_data["state"]  if store_data["state"] else "<MISSING>")
            store.append(store_data["zipCode"] if store_data["zipCode"] else "<MISSING>")
            store.append(store_data["country"])
            store.append(store_data["id"])
            store.append(store_data["phone"] if "phone" in store_data and store_data["phone"] else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            hours = " ".join(list(location_soup.find("table",{"class":"c-location-hours-details"}).stripped_strings))
            store.append(hours if hours != "" else "<MISSING>")
            store.append(url)
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            # print(store)
            yield store
        # if len(data) < MAX_RESULTS:
        #     print("max distance update")
        #     search.max_distance_update(MAX_DISTANCE)
        if len(data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)

scrape()