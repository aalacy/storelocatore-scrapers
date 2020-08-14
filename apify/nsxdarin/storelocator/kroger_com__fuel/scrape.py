import csv
import urllib2
from sgrequests import SgRequests
import sgzip
import json

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()
headers1 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

headers = {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'User-Agent': "PostmanRuntime/7.19.0",
        "content-type": "application/json;charset=UTF-8",
    }

MAX_RESULTS = 50
MAX_DISTANCE = 10

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = set()
    locations = []
    coord = search.next_zip()
    while coord:
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        website = 'kroger.com/fuel'
        #print('%s...' % coord)
        url = 'https://www.kroger.com/stores/api/graphql'
        data = "{\"query\":\"\\n      query storeSearch($searchText: String!, $filters: [String]!) {\\n        storeSearch(searchText: $searchText, filters: $filters) {\\n          stores {\\n            ...storeSearchResult\\n          }\\n          fuel {\\n            ...storeSearchResult\\n          }\\n          shouldShowFuelMessage\\n        }\\n      }\\n      \\n  fragment storeSearchResult on Store {\\n    banner\\n    vanityName\\n    divisionNumber\\n    storeNumber\\n    phoneNumber\\n    showWeeklyAd\\n    showShopThisStoreAndPreferredStoreButtons\\n    storeType\\n    distance\\n    latitude\\n    longitude\\n    tz\\n    ungroupedFormattedHours {\\n      displayName\\n      displayHours\\n      isToday\\n    }\\n    address {\\n      addressLine1\\n      addressLine2\\n      city\\n      countryCode\\n      stateCode\\n      zip\\n    }\\n    pharmacy {\\n      phoneNumber\\n    }\\n    departments {\\n      code\\n    }\\n    fulfillmentMethods{\\n      hasPickup\\n      hasDelivery\\n    }\\n  }\\n\",\"variables\":{\"searchText\":\"" + str(coord) + "\",\"filters\":[]},\"operationName\":\"storeSearch\"}"
        r = session.post(url, headers=headers, data=data)
        result_coords = []
        purl = '<MISSING>'
        typ = 'Gas'
        array = []
        for line in r.iter_lines():
            if '"fuel":' in line and '"fuel":[],' not in line:
                items = line.split('"fuel":')[1].split('"banner":')
                for item in items:
                    if '"vanityName":"' in item:
                        brand = item.split('"vanityName":"')[0]
                        if 'KROGER' in brand:
                            brand = 'KROGER'
                            name = item.split('vanityName":"')[1].split('"')[0]
                            division = item.split('"divisionNumber":"')[1].split('"')[0]
                            #print(name + '|' + division)
                            store = item.split('"storeNumber":"')[1].split('"')[0]
                            try:
                                phone = item.split('"phoneNumber":"')[1].split('"')[0].replace('"','')
                            except:
                                phone = '<MISSING>'
                            lat = item.split('"latitude":"')[1].split('"')[0]
                            lng = item.split('"longitude":"')[1].split('"')[0]
                            add = item.split('"addressLine1":"')[1].split('"')[0]
                            try:
                                add = add + ' ' + item.split('"addressLine2":"')[1].split('"')[0]
                            except:
                                pass
                            website = 'kroger.com/fuel'
                            typ = 'Gas'
                            country = 'US'
                            state = item.split('"stateCode":"')[1].split('"')[0]
                            zc = item.split('"zip":"')[1].split('"')[0]
                            city = item.split('"city":"')[1].split('"')[0]
                            info = add + ';' + city + ';' + state
                            ids.add(info)
                            array.append(info)
                            hours = ''
                            purl = 'https://www.kroger.com/stores/details/' + division + '/' + store
                            r2 = session.get(purl, headers=headers1)
                            for line2 in r2.iter_lines():
                                if 'Store Hours:</span>' in line2:
                                    sinfo = line2.split('Store Hours:</span>')[1].split('></div></div></div>')[0]
                                    days = sinfo.split('class="StoreInformation-day font-medium">')
                                    for day in days:
                                        if '<div class="StoreInformation-dayAndHoursWrapper"' not in day:
                                            hrs = day.split('<')[0] + ': ' + day.split('</span><span>')[1].split('<')[0]
                                            if hours == '':
                                                hours = hrs
                                            else:
                                                hours = hours + '; ' + hrs
                            if info not in locations:
                                if hours == '':
                                    hours = '<MISSING>'
                                if phone == '':
                                    phone = '<MISSING>'
                                locations.append(info)
                                hours = hours.replace(': :',':')
                                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if len(array) <= MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
