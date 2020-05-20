import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
import json
import phonenumbers
from tenacity import retry, stop_after_attempt

def write_output(data):
    with open('data.csv', mode='w',newline = "") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

@retry(stop=stop_after_attempt(7))
def post_data(url, data, headers):
    session = SgRequests()
    return session.post(url, headers=headers,data=data)

@retry(stop=stop_after_attempt(7))
def get_data(url, headers):
    session = SgRequests()
    return session.get(url, headers=headers)

def fetch_data():
    locator_domain = 'https://www.fredmeyer.com/'
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 500
    MAX_DISTANCE = 200
    zip_code = search.next_zip()
    while zip_code:
        result_coords = []
        headers = {
            'User-Agent': "PostmanRuntime/7.19.0",
            'content-type' : 'application/json;charset=UTF-8'
        }
        data = r'{"query":"\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n","variables":{"searchText":"'+str(zip_code)+'","filters":[]},"operationName":"storeSearch"}'
        r = post_data('https://www.frysfood.com/stores/api/graphql', data, headers)
        try:
            datas = r.json()['data']['storeSearch']['stores']
        except:
            continue
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
            location_type = "store"
            latitude = key['latitude'].strip()
            longitude = key['longitude'].strip()
            if "0" == latitude or "0" == longitude or "0.00000000" == latitude or "0.00000000" == longitude:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            page_url = "https://www.fredmeyer.com/stores/details/"+str(key['divisionNumber'])+"/"+str(store_number)
            r_loc = get_data(page_url, headers)
            soup_loc = BeautifulSoup(r_loc.text, "lxml")
            try:
                ltype = soup_loc.find("div", class_="logo").a["title"].strip()
                if "Fred Meyer" in ltype:
                    location_type = ltype
                else:
                    continue
                hours_of_operation = ""
                for day_hours in key["ungroupedFormattedHours"]:
                    hours_of_operation += day_hours["displayName"] + \
                        " = " + day_hours["displayHours"] + "  "
                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

                if str(store[2]) not in addresses and country_code:
                    addresses.append(str(store[2]))

                    store = [str(x).encode('ascii', 'ignore').decode(
                        'ascii').strip() if x else "<MISSING>" for x in store]
                    yield store
            except:
                search.max_distance_update(MAX_DISTANCE)
        if len(datas) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(datas) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()        
