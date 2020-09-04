import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url,headers=headers)
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
                    r = session.post(url,headers=headers,data=data)
                else:
                    r = session.post(url,headers=headers)
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
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    # search.initialize(include_canadian_fsas = True)   # with canada zip
    MAX_RESULTS = 50
    MAX_DISTANCE = 200
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'User-Agent': "PostmanRuntime/7.19.0",
        "content-type": "application/json;charset=UTF-8",
    }

    base_url = "https://www.bakersplus.com"

    while zip_code:
        result_coords = []

        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # print("zip_code === " + zip_code)

        # zip_code = "11576"

        data = "{\"query\":\"\\n      query storeSearch($searchText: String!, $filters: [String]!) {\\n        storeSearch(searchText: $searchText, filters: $filters) {\\n          stores {\\n            ...storeSearchResult\\n          }\\n          fuel {\\n            ...storeSearchResult\\n          }\\n          shouldShowFuelMessage\\n        }\\n      }\\n      \\n  fragment storeSearchResult on Store {\\n    banner\\n    vanityName\\n    divisionNumber\\n    storeNumber\\n    phoneNumber\\n    showWeeklyAd\\n    showShopThisStoreAndPreferredStoreButtons\\n    storeType\\n    distance\\n    latitude\\n    longitude\\n    tz\\n    ungroupedFormattedHours {\\n      displayName\\n      displayHours\\n      isToday\\n    }\\n    address {\\n      addressLine1\\n      addressLine2\\n      city\\n      countryCode\\n      stateCode\\n      zip\\n    }\\n    pharmacy {\\n      phoneNumber\\n    }\\n    departments {\\n      code\\n    }\\n    fulfillmentMethods{\\n      hasPickup\\n      hasDelivery\\n    }\\n  }\\n\",\"variables\":{\"searchText\":\""+str(zip_code)+"\",\"filters\":[]},\"operationName\":\"storeSearch\"}"
        locations_url = "https://www.bakersplus.com/stores/api/graphql"
        r_locations = request_wrapper(locations_url,"post", headers=headers,data=data)

        # print("r_locations.text ==== " + r_locations.text)

        locations_json = r_locations.json()

        current_results_len = len(locations_json["data"]["storeSearch"]["stores"])  # it always need to set total len of record.
        # print("current_results_len === " + str(current_results_len))

        for script in locations_json["data"]["storeSearch"]["stores"]:

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
            page_url = ""
            hours_of_operation = ""

            # do your logic here
            # print('script["address"] === '+ str(script["address"]))

            street_address = script["address"]["addressLine1"]
            if "addressLine2" in script["address"] and script["address"]["addressLine2"]:
                street_address += " "+ script["address"]["addressLine2"]
            city = script["address"]["city"]
            country_code = script["address"]["countryCode"]
            state = script["address"]["stateCode"]
            zipp = script["address"]["zip"]
            phone = script["phoneNumber"]
            #store_number = script["storeNumber"]
            latitude = script["latitude"]
            longitude = script["longitude"]
            #location_type = script["storeType"]
            location_name = script["vanityName"]
            page_url = "https://www.bakersplus.com/stores/details/"+str(script["divisionNumber"])+"/"+str(script["storeNumber"])

            hours_of_operation = ""
            for day_hours in script["ungroupedFormattedHours"]:
                hours_of_operation += day_hours["displayName"] +" = "+day_hours["displayHours"]+"  "

            # print("hours_of_operation == "+ hours_of_operation)

            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

            if str(store[2]) not in addresses and country_code:
                addresses.append(str(store[2]))

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
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
