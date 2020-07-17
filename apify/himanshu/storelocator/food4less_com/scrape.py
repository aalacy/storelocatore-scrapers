import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
import json
import phonenumbers



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.food4less.com/'
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes= ["US","CA"])
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        # print("zip_code === " + str(zip_code))
        # print("ramiang zip =====" + str(len(search.zipcodes)))
        headers = {
            'User-Agent': "PostmanRuntime/7.19.0",
            'content-type' : 'application/json;charset=UTF-8'
        }
        data = r'{"query":"\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n","variables":{"searchText":"'+str(zip_code)+'","filters":[]},"operationName":"storeSearch"}'
        # try:
        r = session.post('https://www.frysfood.com/stores/api/graphql', headers=headers,data=data)
        # except:
        #     continue
        datas = r.json()['data']['storeSearch']['stores']        
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
            if key['banner']:
                location_type = key['banner']
            else:
                location_type = "store"
            latitude = key['latitude']
            longitude = key['longitude']
            result_coords.append((latitude, longitude))
            hours_of_operation = ''
            if key['ungroupedFormattedHours']:
                for hr in  key['ungroupedFormattedHours']:
                    hours_of_operation += hr['displayName']+": "+ hr['displayHours']+", "
            else:
                hours_of_operation =  "<MISSING>"
            page_url = "https://www.food4less.com/stores/details/"+str(key['divisionNumber'])+"/"+str(store_number)
        
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
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',)
            yield store

        ###fuel store
        try:
            datas1 = r.json()['data']['storeSearch']['fuel']
        except:
            continue
        for key1 in datas1:
            location_name = key1['vanityName']
            street_address = key1['address']['addressLine1'].capitalize()
            city = key1['address']['city'].capitalize()
            state = key1['address']['stateCode']
            zipp =  key1['address']['zip']
            country_code = key1['address']['countryCode']
            store_number = key1['storeNumber']
            phone = key1['phoneNumber']
            if key['banner']:
                location_type = key['banner']
            else:
                location_type = "fuel"
            latitude = key1['latitude']
            longitude = key1['longitude']
            result_coords.append((latitude, longitude))
            hours_of_operation = ''
            if key1['ungroupedFormattedHours']:
                for hr in  key1['ungroupedFormattedHours']:
                    hours_of_operation += hr['displayName']+": "+ hr['displayHours']+", "
            else:
                hours_of_operation =  "<MISSING>"
            page_url = "https://www.food4less.com/stores/details/"+str(key1['divisionNumber'])+"/"+str(store_number)
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
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',)
            yield store
    
        if len(datas)+len(datas1) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(datas)+len(datas1) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
