# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip


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
    MAX_RESULTS = 600
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.aarons.com/"

    while coord:
        result_coords = []
        lat = coord[0]
        lng = coord[1]
        # print(search.current_zip)
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        location_url = "https://api.sweetiq.com/store-locator/public/locations/59151b8997c569e45c00e398?categories=&geo%5B0%5D="+str(lng)+"&geo%5B1%5D="+str(lat)+"&tag=&perPage="+str(MAX_RESULTS)+"&search=&searchFields%5B0%5D=name"
        r = requests.get(location_url, headers=headers)
        # r_utf = r.text.encode('ascii', 'ignore').decode('ascii')
        # soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")

        json_data = r.json()
        # json_data = json.loads(r_utf)
        # print("json_Data === " + str(json_data))
        current_results_len = len(json_data["records"])  # it always need to set total len of record.
        # print("current_results_len === " + str(current_results_len))

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

        for location in json_data["records"]:
            # hours_of_operation =''
            # for h in location['hoursOfOperation']:
            #     if location['hoursOfOperation'][h] != []:
            #         hours_of_operation = hours_of_operation + ' ' + h + ' ' + location['hoursOfOperation'][h][-1][0] + ' ' +location['hoursOfOperation'][h][-1][1]

            # print(hours_of_operation)

            # print("location ==== " + str(location))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(location['postalCode']))

            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(location['postalCode']))
            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            # do your logic.
            latitude = str(location['geo'][0])
            # print("latitude ",latitude)
            longitude = str(location['geo'][1])
            page_url = location['website']
            m =(page_url.replace("https://locations.aarons.com/us-il-pekin-2113-court-st-store","https://locations.aarons.com/us-il-pekin-3010-court-st-store")\
            .replace("https://locations.aarons.com/us-il-sterling-4311-e-lincolnway-ste-l-store","https://locations.aarons.com/us-il-sterling-2214-e-4th-st-store")\
            .replace("https://locations.aarons.com/us-il-benton-9-n-rend-lake-plz-store","https://locations.aarons.com/us-il-benton-9-n-rend-lake-plz-store-1")    )
            #print(m)
            r = requests.get(m, headers=headers,  allow_redirects=False)
            soup= BeautifulSoup(r.text,"lxml")
            a = soup.find("div",{"class":"sl-hours"}).text
            hours_of_operation = a.replace("PM","PM ").replace("day","day ")
            #print(hours_of_operation)
            # for y in a:.find_all("div",{"class":"state-container"})[0:51]

            result_coords.append((latitude, longitude))
            store = [locator_domain, location['name'].capitalize(), location['address'].capitalize(), location['city'].capitalize(), location['province'], zipp, country_code,
                     store_number, location['phone'], location_type, location['geo'][1], location['geo'][0], hours_of_operation,m]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

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
