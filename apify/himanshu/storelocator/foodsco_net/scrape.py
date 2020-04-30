import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
import json
import phonenumbers
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w',newline = "") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    locator_domain = 'https://www.foodsco.net/'
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["US"])
    MAX_RESULTS = 500
    MAX_DISTANCE = 200
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        # print("zip_code === " + str(zip_code))
        # print("remaining zip =====" + str(len(search.zipcodes)))
        headers = {
            'User-Agent': "PostmanRuntime/7.19.0",
            'content-type' : 'application/json;charset=UTF-8'
        }
        data = r'{"query":"\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n","variables":{"searchText":"'+str(zip_code)+'","filters":[]},"operationName":"storeSearch"}'
        r = session.post('https://www.foodsco.net/stores/api/graphql', headers=headers,data=data)
        # print(r.text)
        try:
            datas = r.json()['data']['storeSearch']['stores']
        except:
            pass
        for key in datas:
            location_name = key['vanityName']
            street_address = key['address']['addressLine1'].capitalize()
            city = key['address']['city'].capitalize()
            state = key['address']['stateCode']
            zipp =  key['address']['zip']
            country_code = key['address']['countryCode']
            store_number = key['storeNumber']
            if key['phoneNumber']:
                phone = phonenumbers.format_number(phonenumbers.parse(str(key['phoneNumber']), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
            else:
                phone = "<MISSING>"
            # print("store == ",key["pharmacy"],"dept == ",key["departments"])
            # if key["pharmacy"] == None and key["departments"] == []:
            #     storetype = key["storeType"]
            #     print("if === ",str(storetype) )
            # else:
            #     storetype  = key["storeType"]
            #     print("else === ",str(storetype))
            # location_type = "store"
            if key["storeType"] == "F":
                location_type   ="foodsCo"
            else:
                continue
            latitude = key['latitude'].strip()
            longitude = key['longitude'].strip()
            result_coords.append((latitude, longitude))
            hours_of_operation = ''
            if key['ungroupedFormattedHours']:
                for hr in  key['ungroupedFormattedHours']:
                    hours_of_operation += hr['displayName']+": "+ hr['displayHours']+", "
            else:
                hours_of_operation =  "<MISSING>"
            page_url = "https://www.foodsco.net/stores/details/"+str(key['divisionNumber'])+"/"+str(store_number)
            if "0" == latitude or "0" == longitude or "0.00000000" == latitude or "0.00000000" == longitude:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[1] + " "+ store[2]+ " "+ store[9]+" "+store[-1]) not in addresses and country_code:
                addresses.append(str(store[1] + " "+ store[2]+ " "+ store[9]+" "+store[-1]))

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # print("data = " + str(store))
                # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
        if len(datas) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(datas) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
        

        ###fuel store
        # try:
        #     datas1 = r.json()['data']['storeSearch']['fuel']
        # except:
        #     pass
        # for key1 in datas1:
        #     location_name = key1['vanityName']
        #     street_address = key1['address']['addressLine1'].capitalize()
        #     city = key1['address']['city'].capitalize()
        #     state = key1['address']['stateCode']
        #     zipp =  key1['address']['zip']
        #     country_code = key1['address']['countryCode']
        #     store_number = key1['storeNumber']
        #     if key1['phoneNumber']:
        #         phone = phonenumbers.format_number(phonenumbers.parse(str(key1['phoneNumber']), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
        #     else:
        #         phone = "<MISSING>"
        #     location_type = "fuel"
        #     print("fuel === ",key["pharmacy"])
        #     latitude = key1['latitude'].strip()
        #     longitude = key1['longitude'].strip()
        #     result_coords.append((latitude, longitude))
        #     hours_of_operation = ''
        #     if key1['ungroupedFormattedHours']:
        #         for hr in  key1['ungroupedFormattedHours']:
        #             hours_of_operation += hr['displayName']+": "+ hr['displayHours']+", "
        #     else:
        #         hours_of_operation =  "<MISSING>"
        #     page_url = "https://www.foodsco.net/stores/details/"+str(key1['divisionNumber'])+"/"+str(store_number)
        #     if "0" == latitude or "0" == longitude or "0.00000000" == latitude or "0.00000000" == longitude:
        #         latitude = "<MISSING>"
        #         longitude = "<MISSING>"
                
            
        #     store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
        #                      store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        #     if str(store[1] + " "+ store[2]+ " "+ store[9]+" "+store[-1]) not in addresses and country_code:
        #         addresses.append(str(store[1] + " "+ store[2]+ " "+ store[9]+" "+store[-1]))

        #         store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

        #         # print("data = " + str(store))
        #         # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        #         yield store
        # if len(datas)+len(datas1) < MAX_RESULTS:
        #     # print("max distance update")
        #     search.max_distance_update(MAX_DISTANCE)
        # elif len(datas)+len(datas1) == MAX_RESULTS:
        #     # print("max count update")
        #     search.max_count_update(result_coords)
        # else:
        #     raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        # zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
