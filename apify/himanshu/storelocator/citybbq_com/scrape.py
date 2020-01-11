import urllib.parse
import requests
from bs4 import BeautifulSoup
import re
import ast
import json
import sgzip
import csv


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        'User-Agent': "PostmanRuntime/7.19.0",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        'accept': 'application/json, text/javascript, */*; q=0.01',
    }
    # coords = sgzip.coords_for_radius(50)
    search = sgzip.ClosestNSearch()
    search.initialize()
    addresses = []
    MAX_RESULTS = 25
    MAX_DISTANCE = 50
    current_results_len = 0
    coords = search.next_coord()

    while coords:
        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        addresses = []
        result_coords = []
        locator_domain = "https://www.citybbq.com"
        location_name = "<MISSING>"
        street_address = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zipp = "<MISSING>"
        country_code = "<MISSING>"
        store_number = "<MISSING>"
        phone = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"
        page_url = "<MISSING>"

        data = "lat=" + str(coords[0]) + "&lng=" + str(coords[1])
        # data = "lat=33.79&lng=-84.27"
        #print(data)
        try:
            r = requests.post(
                " https://www.citybbq.com/wp-content/themes/city-bbq/api/get-closest-locations.php", headers=headers, data=data).json()

        except:
            continue
        if r != []:
            current_results_len = len(r)
            for loc in r:
                store_number = loc["id"]
                location_name = loc["title"]
                # print(location_name)
                latitude = loc["lat"]
                longitude = loc["lng"]
                street_address = " ".join(loc["address"].split("<br>")[:-1])
                city = loc["address"].split("<br>")[-1].split(",")[0]
                try:
                    sz = loc["address"].split("<br>")[-1].split(",")[1]
                except:
                    pass
                    #print(loc["address"])
                    #print("~~~~~~~~~~~~~~~~~~~~~~")

                us_zip_list = re.findall(re.compile(
                    r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(sz))
                state_list = re.findall(r' ([A-Z]{2}) ', str(sz))
                country_code = "US"
                if us_zip_list:
                    zipp = us_zip_list[-1]

                else:
                    zipp = "<MISSING>"
                if state_list:
                    state = state_list[0]
                else:
                    state = "<MISSING>"
                #print(zipp, state)
                hours_of_operation = loc["hours"].replace("<br>", " ")
                phone = loc["phone"]
                page_url = "https://www.citybbq.com" + loc["order_link"]

                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = [x if x else "<MISSING>" for x in store]
                store = [str(x).encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])

                #print("data = " + str(store))
                #print(
                    # '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
        if current_results_len < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        coords = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
