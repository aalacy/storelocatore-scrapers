import csv
import sgzip
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

headers = {
    # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'User-Agent': "PostmanRuntime/7.19.0",
    "content-type": "application/json;charset=UTF-8",
}

@retry(stop=stop_after_attempt(7))
def post_data(url, data):
    session = SgRequests()
    return session.post(url, headers=headers, data=data).json()

def get_data(url):
    session = SgRequests()
    return session.get(url, headers=headers)

def get_open_hours(script):
    try:
        hours_of_operation = ""
        for day_hours in script["ungroupedFormattedHours"]:
            hours_of_operation += day_hours["displayName"] + \
                " = " + day_hours["displayHours"] + "  "
        return hours_of_operation
    except:
        print("no hours found")
        return None

def compute_key(street_address, city, state, zipp):
    return '-'.join([street_address, city, state, zipp])

def fetch_data():
    return_main_object = []
    keys = set()
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 200
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()
    base_url = "https://www.kroger.com"

    while zip_code:
        result_coords = []
        data = "{\"query\":\"\\n      query storeSearch($searchText: String!, $filters: [String]!) {\\n        storeSearch(searchText: $searchText, filters: $filters) {\\n          stores {\\n            ...storeSearchResult\\n          }\\n          fuel {\\n            ...storeSearchResult\\n          }\\n          shouldShowFuelMessage\\n        }\\n      }\\n      \\n  fragment storeSearchResult on Store {\\n    banner\\n    vanityName\\n    divisionNumber\\n    storeNumber\\n    phoneNumber\\n    showWeeklyAd\\n    showShopThisStoreAndPreferredStoreButtons\\n    storeType\\n    distance\\n    latitude\\n    longitude\\n    tz\\n    ungroupedFormattedHours {\\n      displayName\\n      displayHours\\n      isToday\\n    }\\n    address {\\n      addressLine1\\n      addressLine2\\n      city\\n      countryCode\\n      stateCode\\n      zip\\n    }\\n    pharmacy {\\n      phoneNumber\\n    }\\n    departments {\\n      code\\n    }\\n    fulfillmentMethods{\\n      hasPickup\\n      hasDelivery\\n    }\\n  }\\n\",\"variables\":{\"searchText\":\"" + str(zip_code) + "\",\"filters\":[]},\"operationName\":\"storeSearch\"}"
        locations_url = "https://www.kroger.com/stores/api/graphql"
        locations_json = post_data(locations_url, data)
        
        current_results_len = len(locations_json["data"]["storeSearch"]["stores"])
        print("remaining zipcodes: " + str(len(search.zipcodes)))
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
            location_type = script['banner']
            location_name = script["vanityName"]
            page_url = "https://www.kroger.com/stores/details/" + \
                str(script["divisionNumber"]) + \
                "/" + str(script["storeNumber"])
            hours_of_operation = get_open_hours(script)
            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            key = compute_key(street_address, city, state, zipp)
            if key not in keys:
                keys.add(key)
                store = [str(x).encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]
                yield store
        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
