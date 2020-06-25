import csv
from bs4 import BeautifulSoup
import re
import json
import sgzip
from random import choice
from sgrequests import SgRequests

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8",newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    #print("start")
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes = ["UK"])
    MAX_RESULTS = 500
    MAX_DISTANCE = 5
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()
    addresses = []
    locator_domain = "https://www.betfred.com/"
    addresses = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    result_coords = []
    while zip_code:
        result_coords = []
        url = "https://www.betfred.com/services/gis/searchstores"
        payload = "{\"SearchLocation\":\" "+str(zip_code)+", UK\",\"MaximumShops\":10,\"MaximumDistance\":5}"
        headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36",
            'Accept': "*/*",
            'Content-Type': "application/json",
            'Cache-Control': "no-cache",
            'Postman-Token': "3c1ecc49-46ce-46e0-9b1e-fdbe4cc065f2,fe8dde9f-a9f4-4533-93bc-31dc8ea517fa",
            'Host': "www.betfred.com",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
            }
        try:
            response = session.post(url, data=payload, headers=headers).json()
            if response["Stores"]:
                current_results_len=len(response["Stores"])
                for loc in response["Stores"]:
                    store_number = loc["ShopNumber"]
                    location_name = loc["Title"]
                    if len(loc["Address"].split(",")) > 1:
                        street_address = " ".join(loc["Address"].split(",")[:-1]).strip()
                        city = loc["Address"].split(",")[-1].strip()
                        # raw_address = "<MISSING>"
                    elif len(loc["Address"].split("  ")) > 1:
                        
                        # Berryden Retail Park  Berryden
                        street_address =" ".join(loc["Address"].split("  ")[:-1]).strip()
                        city = loc["Address"].split("  ")[-1]
                    else:
                        #print(loc["Address"])
                        street_address = loc["Address"]
                        city = "<MISSING>"
                    # street_address = "<INACCESSIBLE>"
                    # city = "<INACCESSIBLE>"
                    state = "<MISSING>"
                    zipp = loc["Postcode"]
                    country_code = "UK"
                    phone = "<MISSING>"
                    latitude = loc["Location"]["Latitude"]
                    longitude = loc["Location"]["Longitude"]
                    hours_of_operation = loc["OpeningHoursDescription"].replace("\r\n","").strip()
                    location_type = "<MISSING>"
                    page_url = "https://www.betfred.com/shop-locator"
                    # raw_address = loc["Address"]
                    result_coords.append((latitude, longitude))
                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    if store_number not in addresses:
                        addresses.append(store_number)

                        store = [str(x).encode('ascii','ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                        # print("data = " + str(store))
                        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                        yield store
        except:
            search.max_distance_update(MAX_DISTANCE)
            # continue        
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
