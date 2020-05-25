import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import sgzip
import json
import phonenumbers
from ssl import SSLError
import time

show_logs = False

session = SgRequests()

post_headers = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,la;q=0.8',
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    'content-type': 'application/json;charset=UTF-8',
    'origin': 'https://www.fredmeyer.com',
    'referer': 'https://www.fredmeyer.com/stores/search',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin'
}

get_headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.9,la;q=0.8',
    'cache-control': 'max-age=0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1'
}


def write_output(data):
    with open('data.csv', mode='w', newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def log(*args, **kwargs):
  if (show_logs == True):
    print(" ".join(map(str, args)), **kwargs)


def post_data(url, data, headers):
    return session.post(url, headers=headers, data=data)


def get_data(url, headers):
    global session
    try:
      response = session.get(url, headers=headers)
      return response
    except SSLError as ssl_err:
      # attempt to handle "sslv3 alert bad record mac"
      print("SSLError: {0}".format(ssl_err))
      print('resetting session')
      session = SgRequests()
      initialize_session()
      return get_data(url, headers)


def initialize_session():
  # get the initial search page to populate session cookies
  url = 'https://www.fredmeyer.com/stores/search'
  log('getting ' + url)
  r = get_data(url, headers=get_headers)
  log(r.status_code)


def isFredMeyerLocation(page_url):
  # check the location detail page for location type
  r_loc = get_data(page_url, headers=get_headers)
  log(page_url, r_loc.status_code)

  soup_loc = BeautifulSoup(r_loc.text, "lxml")
  logo_links = soup_loc.select('div.logo a')

  if len(logo_links) > 0:
    ltype = logo_links[0]["title"].strip()
    if "Fred Meyer" in ltype:
      log(f'found Fred Meyer via logo link title: {ltype}')
      return True
    else:
      log(f'not Fred Meyer in logo link title: {ltype}')
      return False
  else:
    log('cannot find logo link, trying ld+json')

    ldjson = soup_loc.find('script', {'type': 'application/ld+json'})
    if not ldjson:
      log('no ld+json found')
      return False

    jso = json.loads(ldjson.text)
    if "Fred Meyer" in jso["name"]:
      log('found Fred Meyer in ld+json')
      return True
    else:
      log(f'not Fred Meyer in ld+json name: {jso["name"]}')
      return False


def fetch_data():

    locator_domain = 'https://www.fredmeyer.com/'
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()

    zip_code = search.next_zip()
    log('next zip: ', zip_code)

    initialize_session()

    while zip_code:
        result_coords = []
        data = r'{"query":"\n      query storeSearch($searchText: String!, $filters: [String]!) {\n        storeSearch(searchText: $searchText, filters: $filters) {\n          stores {\n            ...storeSearchResult\n          }\n          fuel {\n            ...storeSearchResult\n          }\n          shouldShowFuelMessage\n        }\n      }\n      \n  fragment storeSearchResult on Store {\n    banner\n    vanityName\n    divisionNumber\n    storeNumber\n    phoneNumber\n    showWeeklyAd\n    showShopThisStoreAndPreferredStoreButtons\n    storeType\n    distance\n    latitude\n    longitude\n    tz\n    ungroupedFormattedHours {\n      displayName\n      displayHours\n      isToday\n    }\n    address {\n      addressLine1\n      addressLine2\n      city\n      countryCode\n      stateCode\n      zip\n    }\n    pharmacy {\n      phoneNumber\n    }\n    departments {\n      code\n    }\n    fulfillmentMethods{\n      hasPickup\n      hasDelivery\n    }\n  }\n","variables":{"searchText":"'+str(zip_code)+'","filters":[]},"operationName":"storeSearch"}'

        log(f'doing search for {zip_code}')
        datas = []
        try:
          r = post_data('https://www.fredmeyer.com/stores/api/graphql',
                        data, headers=post_headers)
          r.raise_for_status()
          json = r.json()
          datas = json['data']['storeSearch']['stores']
        except Exception as err:
          print(f'zip: {zip_code}\n status code: {r.status_code}\n json: {json}\n error: {err}')

        log(f'results for {zip_code} -- status: {r.status_code}, locations: {len(datas)}')

        for key in datas:
            location_name = key['vanityName']
            street_address = key['address']['addressLine1'].capitalize()
            city = key['address']['city'].capitalize()
            state = key['address']['stateCode']
            zipp = key['address']['zip']
            country_code = key['address']['countryCode']
            store_number = key['storeNumber']
            if key['phoneNumber']:
                phone = phonenumbers.format_number(phonenumbers.parse(
                    str(key['phoneNumber']), 'US'), phonenumbers.PhoneNumberFormat.NATIONAL)
            else:
                phone = "<MISSING>"
            location_type = "store"
            latitude = key['latitude'].strip()
            longitude = key['longitude'].strip()
            result_coords.append((latitude, longitude))
            if "0" == latitude or "0" == longitude or "0.00000000" == latitude or "0.00000000" == longitude:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            page_url = "https://www.fredmeyer.com/stores/details/" + \
                str(key['divisionNumber'])+"/"+str(store_number)

            if key["banner"] == "FREDMEYER":
              location_type = "Fred Meyer"
              log('found Fred via banner')
              log('------------')
            elif key["banner"] is None and isFredMeyerLocation(page_url):
              location_type = "Fred Meyer"
              log('found Fred via location detail page')
              log('------------')
            else:
              log(f'skipping banner {key["banner"]}')
              log('------------')
              continue

            hours_of_operation = ""
            for day_hours in key["ungroupedFormattedHours"]:
                hours_of_operation += day_hours["displayName"] + \
                    " = " + day_hours["displayHours"] + "  "

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[2]) not in addresses and country_code:
                addresses.append(str(store[2]))

                store = [str(x).encode('ascii', 'ignore').decode(
                    'ascii').strip() if x else "<MISSING>" for x in store]

                log(store)
                yield store

        # log('result_coords', result_coords)
        search.max_count_update(result_coords)
        zip_code = search.next_zip()


def scrape():
    data = fetch_data()
    write_output(data)


log('starting scrape')
tic = time.perf_counter()
scrape()
toc = time.perf_counter()
log(f"done in {toc - tic:0.4f} seconds")
