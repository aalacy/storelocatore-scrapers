# coding=UTF-8
import csv
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time
import requests
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
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
    MAX_RESULTS = 1000
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()
    headers = {
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
                'Accept': "application/json, text/plain, */*",
                'Content-Type': "application/json; charset=UTF-8",
                'Cache-Control': "no-cache",
                'Postman-Token': "b15101fa-fad9-40bd-ae46-a16720e8afc8,59f80690-1b85-4654-adee-313ecbdfd7d6",
                'Host': "www.walgreens.com",
                'Accept-Encoding': "gzip, deflate",
                'Content-Length': "101",
                # 'Cookie': "dtCookie=6$A3425DF8397009D51DBAAA43E235903D; bm_sz=F124BF48E16D20D9D57CDBC52FD9C434~YAAQdzYauK+WoglyAQAAXQ9mJwesiiUOaw4YE4q30HDpCIiq2pitnMem0H9mz2D8rYmMd9rOQCtFHN8qj9AW9GjvNCqGEtnokcC2TnCNKqH/pe4wKyv5NFQuB1lWD/cdulHeRlH0IVHW9071vRsqNmFwAuaIHH18RSjUaQxdVMpNjJWTZptV+bCLGFRKDNc8LH0T; _abck=5A86A806EC7840014A3875C784EF84EA~-1~YAAQdzYauLCWoglyAQAAXQ9mJwMLS6oEE75LWvrjEqe00QAWRF+GNIGc+41AMs4q60iQMir0xCjU4thqnvSltFyOcVrGbsN+r94vzGlKwtQJ3AGyNhXSatWR4iS/OHFV6hoa+GULFQWaUyRoEYZXo7IsdL0VEtweS90nH/5kR3tB0GeGcPqdLHmlNNFx5jQAsvwGgLxP1YYrQGbNG9KVCXp6g9vsOzHsSJCG/IbMwcpxozAvfc25ObkMBQIN1+xJekV2ZWKCWF7pKHm5x1WVR9F6/8kQrT/CJJaoQ8xSd7+b0ZwlgZKuppUbyNxT~-1~-1~-1",
                'Connection': "keep-alive",
                'cache-control': "no-cache"
                }
    base_url = "https://www.walgreens.com"
    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        # print(search.zipcode)
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        page = 1
        while True:
            url = "https://www.walgreens.com/locator/v1/stores/search"

            querystring = {"requestor":"search"}

            payload = "{\"q\":\"\",\"r\": \"50\", \"lat\": "+str(lat)+", \"lng\":"+str(lng)+", \"requestType\": \"dotcom\", \"s\": \"20\", \"p\": "+str(page)+"}"
            
            r = requests.request("POST", url, data=payload, headers=headers, params=querystring).json()
            
            if "results" not in r:
                break
            current_results_len= len(r['results'])
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
                try:
                    r1 = requests.get(page_url ,headers=headers)
                except:
                    pass
                soup = BeautifulSoup(r1.text,"lxml")
                try:
                    hours_of_operation = " ".join(list(soup.find("div",{"class":'service-section'}).find("li",{"class":'single-hours-lists'}).stripped_strings))
                except:
                    hours_of_operation = "<MISSING>"

                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, location['store']['address']['street'].capitalize(), location['store']['address']['city'].capitalize(), location['store']['address']['state'], zipp, country_code,
                        storeNumber, phone.strip(), location_type, latitude, longitude, hours_of_operation,page_url]

                if str(store[-7]) in addresses:
                    continue
                addresses.append(str(store[-7]) )
                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                # print("data =="+str(store))
                # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
                yield store
            page+=1
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

        
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
