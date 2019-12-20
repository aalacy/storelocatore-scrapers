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
    MAX_RESULTS = 100
    MAX_DISTANCE = 10
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'content-type': 'application/json',
    }

    base_url = "https://www.deadriver.com"

    while zip_code:
        result_coords = []

        #print("remaining zipcodes: " + str(len(search.zipcodes)))
        #print("zip_code === " + zip_code)

        location_url = "https://www.deadriver.com/LocationFinder.asmx/GetLocation"
        # print("location url = "+ location_url +'{"zipCode":"' + zip_code + '"}')

        r = requests.post(location_url, headers=headers, data='{"zipCode":"' + zip_code + '"}')

        # print("text_data ==== " + str(r.text))

        soup = BeautifulSoup(r.text, "lxml")
        text_data = soup.find("p").text.replace('"[', "[").replace(']"', ']').replace('\\\\\\"',"'").replace('\\','')

        # print("text_data ==== " + str(text_data))
        json_data = json.loads(text_data)  # BeautifulSoup(r.text, "xml")

        if json_data["d"]:
            current_results_len = len(json_data["d"])
        else:
            current_results_len = 0

        # print("current_results_len ===  " + str(current_results_len))

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""

        if current_results_len > 0:
            for location in json_data["d"]:
               # print(location)
                street_address = location["AddressOne"] + " " + location["AddressTwo"]
                city = location["City"]
                zipp = location["ZipCode"]
                state = location["State"]
                # print(zipp)
                phone = location["PhoneOne"]
                longitude = location["Longitude"]
                latitude = location["Latitude"]
                location_name = location["CompanyName"]
                # do your logic.
                page_url = "<MISSING>"

                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

                if str(store[2]) + str(store[-3]) not in addresses:
                    addresses.append(str(store[2]) + str(store[-3]))

                    store = [x if x else "<MISSING>" for x in store]

                    # return_main_object.append(store)
                    yield store
                    print("data = " + str(store))
                    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

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
