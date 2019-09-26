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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.shopmyexchange.com"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        # print('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        location_url = "https://www.shopmyexchange.com/stores"

        # print("location url = "+ location_url +'{"longitude": '+str(lat)+', "latitude": '+str(lng)+'}')
        # lat = -73.6506776
        # lng = 40.7987048
        r = requests.post(location_url, headers=headers, data={"longitude": str(lng), "latitude": str(lat)})

        # r_ascii = r.text.encode('ascii', 'ignore').decode('ascii')

        soup = BeautifulSoup(r.text, "lxml")

        # print("soup ===== "+ str(soup))

        current_results_len = len(soup.find_all("div", {"class": "address"}))  # it always need to set total len of record.
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
        location_type = "shopmyexchange"
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""

        if current_results_len > 0:
            for script in soup.find_all("div", {"class": "result pt-1"}):

                full_address = list(script.find("div", {"class": "address"}).stripped_strings)
                street_address = ", ".join(full_address[:-1])
                city = full_address[-1].split(",")[0]
                state = full_address[-1].split(",")[1].replace('\xa0', " ").strip().split(" ")[0]
                zipp = " ".join(full_address[-1].split(",")[1].replace('\xa0', " ").strip().split(" ")[1:]).strip()

                temp_zipp = zipp
                temp_zipp = temp_zipp.replace("-","")

                if (temp_zipp.isdigit()):
                    country_code = "US"
                else:
                    country_code = "CA"

                # print("CSZ == "+full_address[-1].split(",")[1].replace('\xa0', " "))
                # print("city == "+city)
                # print("state == "+state)
                # print("zipp == "+zipp)
                # print("country_code == "+country_code)

                phone = script.find("div", {"class": "phone"}).find("a").text.split("/")[0]

                geo_location = script.find("div", {"class": "address"}).find('a')['onclick']
                latitude = geo_location.split("gotoGoogleDirections(")[1].split(",")[0]
                longitude = geo_location.split("gotoGoogleDirections(")[1].split(",")[1].replace(")", "")

                hours_of_operation = " ".join(list(script.find("div", {"class": "schedule"}).stripped_strings))
                location_name = script.find("div", {"class": "aafes-item-name m-0"}).text

                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]

                if str(store[2]) + str(store[-3]) not in addresses:
                    addresses.append(str(store[2]) + str(store[-3]))

                    store = [x if x else "<MISSING>" for x in store]

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
