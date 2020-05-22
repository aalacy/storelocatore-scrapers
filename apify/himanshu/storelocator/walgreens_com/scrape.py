# coding=UTF-8
import csv
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
import requests
from concurrent.futures import ThreadPoolExecutor

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        
        for row in data:
            writer.writerow(row)


def get_url(data):
    headers = {
        'Content-Type': 'application/json'
    }
    url = "https://www.walgreens.com/locator/v1/stores/search?requestor=search"
    data = requests.post(url,data=data,headers=headers)
    try:
        return data
    except:
        pass

def _send_multiple_rq(vk):
    with ThreadPoolExecutor(max_workers=len(vk)) as pool:
        # for data in list(pool.map(get_url,list_of_urls)):
        return list(pool.map(get_url,vk))
                # print(data.text)

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 1000
    MAX_DISTANCE = 25
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()
    headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
                'Accept': "application/json, text/plain, */*",
                'Content-Type': "application/json; charset=UTF-8",
                'Cache-Control': "no-cache",
                'Postman-Token': "b15101fa-fad9-40bd-ae46-a16720e8afc8,59f80690-1b85-4654-adee-313ecbdfd7d6",
                'Host': "www.walgreens.com",
                'Accept-Encoding': "gzip, deflate",
                'Content-Length': "101",
                'Connection': "keep-alive",
                'cache-control': "no-cache"
                }
    base_url = "https://www.walgreens.com"
    list_of_urls=[]
    # list_of_urls.append( "{\"r\":\"1000\",\"zip\":%s,\"requestType\":\"dotcom\",\"s\":\"1000\"}"%('"{}"'.format(str(85029))))
    while zip_code:
        result_coords = []
        print(zip_code)
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        # page = 1
        list_of_urls.append( "{\"r\":\"1000\",\"zip\":%s,\"requestType\":\"dotcom\",\"s\":\"1000\"}"%('"{}"'.format(str(zip_code))))        
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()

    # print("len---- ",len(list_of_urls))
    data = _send_multiple_rq(list_of_urls)
    for q in data:
        r= q.json()
        if "results" in r:
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
            for location in r["results"]:
                storeNumber = location['store']['storeNumber']
                location_name = "Walgreens - Store #"+str(storeNumber)
                phone =location['store']['phone']['areaCode'] + ' '+ location['store']['phone']['number']
                storeNumber = location['storeNumber']
                latitude = location['latitude']
                longitude = location['longitude']
                zipp = location['store']['address']['zip']
                if zipp.replace("-","").strip().isdigit():
                    country_code = "US"
                else:
                    country_code = "CA"
                if phone.strip().lstrip():
                    phone = phone
                else:
                    phone = "<MISSING>"  
                page_url = "https://www.walgreens.com"+location['storeSeoUrl']
                # try:
                #     r1 = requests.get(page_url ,headers=headers)
                # except:
                #     pass
                # soup = BeautifulSoup(r1.text,"lxml")
                # try:
                #     hours_of_operation = " ".join(list(soup.find("div",{"class":'service-section'}).find("li",{"class":'single-hours-lists'}).stripped_strings))
                # except:
                hours_of_operation = "<MISSING>"

                store = [locator_domain, location_name, location['store']['address']['street'].capitalize(), location['store']['address']['city'].capitalize(), location['store']['address']['state'], zipp, country_code,
                        storeNumber, phone.strip(), location_type, latitude, longitude, hours_of_operation,page_url]

                if str(store[2]) in addresses:
                    continue
                addresses.append(str(store[2]) )
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                print("data =="+str(store))
                print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store


def scrape():
    data = fetch_data()
    write_output(data)
scrape()
