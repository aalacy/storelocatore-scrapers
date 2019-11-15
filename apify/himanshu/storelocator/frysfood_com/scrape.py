import csv
import requests
from bs4 import BeautifulSoup
import re
import sgzip
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)





def fetch_data():
    addresses1 = []
    base_url = "https://www.frysfood.com/"
    locator_domain = 'https://www.frysfood.com'
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 100
    coords = search.next_coord()
    return_main_object = []
    while coords:
        result_coords = []
        # print("zip_code === " + str(coords))
        #print("ramiang zip =====" + str(len(search.zipcodes)))
        headers = {
            'User-Agent': "PostmanRuntime/7.19.0",
            'content-type' : 'application/json;charset=UTF-8'
        }
        data = r'{"query":"\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n","variables":{"searchText":"'+str(search.current_zip)+'","filters":[]},"operationName":"storeSearch"}'
        r = requests.post('https://www.frysfood.com/stores/api/graphql', headers=headers,data=data)
        datas = r.json()['data']['storeSearch']['stores']
        # print(datas)
        for key in datas:
            location_name = key['vanityName']
            street_address = key['address']['addressLine1']
            city = key['address']['city']
            state = key['address']['stateCode']
            zipp =  key['address']['zip']
            country_code = key['address']['countryCode']
            store_number = '<MISSING>'
            phone = key['phoneNumber']
            location_type = "<MISSING>"
            latitude = key['latitude']
            longitude = key['longitude']
            result_coords.append((latitude, longitude))
            hours_of_operation = ''
            if key['ungroupedFormattedHours']:
                for hr in  key['ungroupedFormattedHours']:
                    hours_of_operation += hr['displayName']+": "+ hr['displayHours']+", "
            else:
                hours_of_operation =  "<MISSING>"
            page_url = "<MISSING>"

        
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zipp if zipp else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append("<MISSING>")
            if store[2] in addresses1:
                continue
            addresses1.append(store[2])
            # print("data = " + str(store)
            #print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',  str(store))
            yield store
            # print(return_object)

        if len(datas) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(datas) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
