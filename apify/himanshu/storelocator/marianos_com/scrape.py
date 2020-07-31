import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_DISTANCE = 200
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': "PostmanRuntime/7.19.0",
        "content-type": "application/json;charset=UTF-8",
    }

    base_url = "http://marianos.com/"

    while zip_code:
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        result_coords = []
        data = "{\"query\":\"\\n      query storeSearch($searchText: String!, $filters: [String]!) {\\n        storeSearch(searchText: $searchText, filters: $filters) {\\n          stores {\\n            ...storeSearchResult\\n          }\\n          fuel {\\n            ...storeSearchResult\\n          }\\n          shouldShowFuelMessage\\n        }\\n      }\\n      \\n  fragment storeSearchResult on Store {\\n    banner\\n    vanityName\\n    divisionNumber\\n    storeNumber\\n    phoneNumber\\n    showWeeklyAd\\n    showShopThisStoreAndPreferredStoreButtons\\n    storeType\\n    distance\\n    latitude\\n    longitude\\n    tz\\n    ungroupedFormattedHours {\\n      displayName\\n      displayHours\\n      isToday\\n    }\\n    address {\\n      addressLine1\\n      addressLine2\\n      city\\n      countryCode\\n      stateCode\\n      zip\\n    }\\n    pharmacy {\\n      phoneNumber\\n    }\\n    departments {\\n      code\\n    }\\n    fulfillmentMethods{\\n      hasPickup\\n      hasDelivery\\n    }\\n  }\\n\",\"variables\":{\"searchText\":\"" + str(zip_code) + "\",\"filters\":[]},\"operationName\":\"storeSearch\"}"
        locations_url = "https://www.marianos.com/stores/api/graphql"
        r_locations = session.post(locations_url, headers=headers, data=data)
        locations_json = r_locations.json()["data"]["storeSearch"]["stores"]
        current_results_len = len(locations_json)
        for script in locations_json:
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

            street_address = script["address"]["addressLine1"]
            if "addressLine2" in script["address"] and script["address"]["addressLine2"]:
                street_address += " " + script["address"]["addressLine2"]
            city = script["address"]["city"]
            country_code = script["address"]["countryCode"]
            state = script["address"]["stateCode"]
            zipp = script["address"]["zip"]
            phone = script["phoneNumber"]
            store_number = script["storeNumber"]
            latitude = script["latitude"]
            longitude = script["longitude"]
            result_coords.append((latitude, longitude))
            location_name = script["vanityName"]
            location_type = script['banner']
            page_url = "https://www.marianos.com/stores/details/" +str(script["divisionNumber"]) +"/" + str(script["storeNumber"])
            hours_of_operation = ""
            for day_hours in script["ungroupedFormattedHours"]:
                hours_of_operation += day_hours["displayName"] +  " = " + day_hours["displayHours"] + "  "
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code, store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            if location_type == 'MARIANOS' and str(store[2]) not in addresses and country_code:
                addresses.append(str(store[2]))
                store = [str(x).encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]
                yield store
        if current_results_len == 0:
            search.max_distance_update(MAX_DISTANCE)
        else:
            search.max_count_update(result_coords)
        zip_code = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
