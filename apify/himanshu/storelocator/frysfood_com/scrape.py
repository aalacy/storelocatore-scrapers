from requests.exceptions import RequestException
import csv
from sgrequests import SgRequests
import re
import sgzip
import json

# import logging
# logging.basicConfig(level=logging.DEBUG)

show_logs = False


def log(*args, **kwargs):
  if (show_logs == True):
    logger.info(" ".join(map(str, args)), **kwargs)


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


def override_retries():
    # monkey patch sgrequests in order to set max retries ...
    # we will control retries in this script in order to reset the session and get a new IP each time
    import requests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('frysfood_com')



    def new_init(self):
        requests.packages.urllib3.disable_warnings()
        self.session = self.requests_retry_session(retries=0)
    SgRequests.__init__ = new_init


def do_search(zip_code, attempts=0):
    global session
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,la;q=0.8',
        'cache-control': 'no-cache',
        'content-type': 'application/json;charset=UTF-8',
        'origin': 'https://www.frysfood.com',
        'pragma': 'no-cache',
        'referer': 'https://www.frysfood.com/stores/search',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
        'x-dtpc': '7$31030907_447h26vWSKTEEVGLSJVMPJLLDTDQKJHRRRORHMM-0',
        'x-dtreferer': 'https://www.frysfood.com/stores/search?searchText=64433'
    }

    data = r'{"query":"\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n","variables":{"searchText":"'+str(zip_code)+'","filters":[]},"operationName":"storeSearch"}'

    max_attempts = 10
    if attempts > max_attempts:
        raise SystemExit(
            f'Exceeded max attempts ({max_attempts}) searching zip code: {zip_code}')

    try:
        r = session.post(
            'https://www.frysfood.com/stores/api/graphql', headers=headers, data=data)
        r.raise_for_status()
        return r
    except RequestException as ex:
        log("--- RequestException -->", ex)
        log("--- Resetting session ...")
        # reset the session and try again
        session = SgRequests()
        # check IP if logging enabled
        if show_logs:
            r = session.get('https://jsonip.com/')
            log(f"--- New IP for session: {r.json()['ip']}")
        search_page_init()
        return do_search(zip_code, attempts+1)


def search_page_init(attempts=0):
    global session
    log("getting initial search page")
    max_attempts = 10
    if attempts > max_attempts:
        raise SystemExit(
            f'Exceeded max attempts ({max_attempts}) getting initial search page')
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9,la;q=0.8',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
        'upgrade-insecure-requests': '1'
    }
    try:
        r = session.get(
            'https://www.frysfood.com/stores/search', headers=headers)
        r.raise_for_status()
        log(f'status code for search_page_init(): {r.status_code}')
    except RequestException as ex:
        log("--- RequestException -->", ex)
        log("--- Resetting session ...")
        # reset the session and try again
        session = SgRequests()
        # check IP if logging enabled
        if show_logs:
            r = session.get('https://jsonip.com/')
            log(f"--- New IP for session: {r.json()['ip']}")
        search_page_init(attempts+1)


def fetch_data():
    locator_domain = 'https://www.frysfood.com'
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=["US", "CA"])
    MAX_RESULTS = 100
    MAX_DISTANCE = 100
    zip_code = search.next_zip()

    search_page_init()

    while zip_code:
        result_coords = []
        log("zip_code: " + str(zip_code))
        log("remaining zips: " + str(search.zipcodes_remaining()))

        r = do_search(zip_code)
        log('status code for do_search(): ', r.status_code)

        datas = []
        try:
            datas = r.json()['data']['storeSearch']['stores']
        except Exception as ex:
            log(
                f'-------- exception parsing stores json for zip {zip_code} --------', ex, '---------')
            # pass

        for key in datas:
            location_name = key['vanityName']
            street_address = key['address']['addressLine1']
            city = key['address']['city']
            state = key['address']['stateCode']
            zipp = key['address']['zip']
            country_code = key['address']['countryCode']
            store_number = key['storeNumber']
            phone = key['phoneNumber']
            location_type = "store"
            latitude = key['latitude']
            longitude = key['longitude']
            result_coords.append((latitude, longitude))
            hours_of_operation = ''
            if key['ungroupedFormattedHours']:
                for hr in key['ungroupedFormattedHours']:
                    hours_of_operation += hr['displayName'] + \
                        ": " + hr['displayHours']+", "
            else:
                hours_of_operation = "<MISSING>"
            page_url = "https://www.frysfood.com/stores/details/" + \
                str(key['divisionNumber'])+"/"+str(store_number)
            log(f'store loc: {page_url}')
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
            store.append(
                hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url)
            if store[2] in addresses:
                log(f'already have store {store[2]}')
                continue
            addresses.append(store[2])
            log("data = " + str(store))
            log('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',)
            yield store

        ###fuel store
        datas1 = []
        try:
            datas1 = r.json()['data']['storeSearch']['fuel']
        except Exception as ex:
            log(
                f'-------- exception parsing fuel stores for zip {zip_code} --------', ex, '---------')
            # pass

        for key1 in datas1:
            location_name = key1['vanityName']
            street_address = key1['address']['addressLine1']
            city = key1['address']['city']
            state = key1['address']['stateCode']
            zipp = key1['address']['zip']
            country_code = key1['address']['countryCode']
            store_number = key1['storeNumber']
            phone = key1['phoneNumber']
            location_type = "fuel"
            latitude = key1['latitude']
            longitude = key1['longitude']
            result_coords.append((latitude, longitude))
            hours_of_operation = ''
            if key1['ungroupedFormattedHours']:
                for hr in key1['ungroupedFormattedHours']:
                    hours_of_operation += hr['displayName'] + \
                        ": " + hr['displayHours']+", "
            else:
                hours_of_operation = "<MISSING>"
            page_url = "https://www.frysfood.com/stores/details/" + \
                str(key1['divisionNumber'])+"/"+str(store_number)
            log(f'fuel loc: {page_url}')
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
            store.append(
                hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url)
            if store[2] in addresses:
                log(f'already have fuel store {store[2]}')
                continue
            addresses.append(store[2])
            log("data = " + str(store))
            log('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',)
            yield store

        final_data = datas + datas1
        if len(final_data) < MAX_RESULTS:
            log("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(final_data) == MAX_RESULTS:
            log("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " +
                            str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


override_retries()
session = SgRequests()
scrape()
