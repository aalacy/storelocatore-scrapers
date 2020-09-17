import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    headers = {
        'Accept': 'application/json;v=1',
        'Host': 'api.capitalone.com',
        'Origin':'https://locations.capitalone.com',
        'Content-Type': 'application/json',
        'Referer': 'https://locations.capitalone.com/?map=39.2705051107681,-76.65074121777727,11z&locTypes=atm,branch,cafe&place=Baltimore,%20MD%2021216,%20USA&servicesFilter=',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36'
        }

    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 50.0
    coord = search.next_coord()
    while coord:

        result_coords = []
        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
       # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        

        payload_branch_atm = '{\"variables\":{\"input\":{\"lat\":' + str(x) + ',\"long\":' + str(y) + ',\"radius\":50,\"locTypes\":[\"cafe\",\"branch\",\"atm\"],\"servicesFilter\":[]}},\"query\":\"\\n        query geoSearch($input: GeoSearchInput!){\\n          geoSearch(input: $input){\\n            locType\\n            locationName\\n            locationId\\n            address {\\n              addressLine1\\n              stateCode\\n              postalCode\\n              city\\n            }\\n            services\\n            distance\\n            latitude\\n            longitude\\n            slug\\n            seoType\\n      ... on Atm {\\n        open24Hours\\n      }\\n\\t    ... on Branch {\\n        phoneNumber\\n        timezone\\n\\t\\t    lobbyHours {\\n\\t\\t\\t    day\\n\\t\\t\\t    open\\n          close\\n\\t\\t    }\\n\\t\\t    driveUpHours {\\n\\t\\t\\t    day\\n\\t\\t\\t    open\\n\\t\\t\\t    close\\n        }\\n        temporaryMessage\\n\\t    }\\n\\t    ... on Cafe {\\n        phoneNumber\\n        photo\\n        timezone\\n\\t\\t    hours {\\n\\t\\t\\t    day\\n\\t\\t\\t    open\\n\\t\\t\\t    close\\n        }\\n        temporaryMessage\\n      }\\n          }\\n        }\"}'
        branch_atm = session.post("https://api.capitalone.com/locations",headers=headers,data=payload_branch_atm)
        json_data = branch_atm.json()
        for value in json_data['data']['geoSearch']:
            locator_domain = "https://www.capitalone.com/"
            location_name = value['locationName']
            street_address = value['address']['addressLine1']
            city = value['address']['city']
            state = value['address']['stateCode']
            zipp = value['address']['postalCode']
            country_code = "US"
            try:
                phone = value['phoneNumber']
            except:
                phone = "<MISSING>"

            location_type = value['locType']
            # print(location_name,location_type)
            lat = value['latitude']
            lng = value['longitude']
           
            
            if location_type == "branch":
                hoo = []
                store_number = value['locationId']
                for i in value['lobbyHours']:
                    day = i['day']
                    op = i['open'].replace(" ","")
                    cl = i['close'].replace(" ","")
                    frame = day + ':' + op + ' - ' + cl
                    hoo.append(frame)
                hours_of_operation = ', '.join(hoo)
            elif location_type == "cafe":
                hoo = []
                store_number = value['locationId']
                for i in value['hours']:
                    day = i['day']
                    op = i['open'].replace(" ","")
                    cl = i['close'].replace(" ","")
                    frame = day + ':' + op + ' - ' + cl
                    hoo.append(frame)
                hours_of_operation = ', '.join(hoo)
            else:
                store_number = "<MISSING>"
                hours_of_operation = "<MISSING>"

            result_coords.append((lat,lng))
            store = []
            store.append(locator_domain)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(lat)
            store.append(lng)
            store.append(hours_of_operation)
            store.append("<MISSING>")
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store
        

        payload_allatm = '{\"variables\":{\"input\":{\"lat\":'+ str(x) + ',\"long\":' + str(y) + ',\"radius\":50,\"locTypes\":[\"atm\",\"allPointAtm\",\"branch\",\"cafe\"],\"servicesFilter\":[]}},\"query\":\"\\n        query geoSearch($input: GeoSearchInput!){\\n          geoSearch(input: $input){\\n            locType\\n            locationName\\n            locationId\\n            address {\\n              addressLine1\\n              stateCode\\n              postalCode\\n              city\\n            }\\n            services\\n            distance\\n            latitude\\n            longitude\\n            slug\\n            seoType\\n      ... on Atm {\\n        open24Hours\\n      }\\n\\t    ... on Branch {\\n        phoneNumber\\n        timezone\\n\\t\\t    lobbyHours {\\n\\t\\t\\t    day\\n\\t\\t\\t    open\\n          close\\n\\t\\t    }\\n\\t\\t    driveUpHours {\\n\\t\\t\\t    day\\n\\t\\t\\t    open\\n\\t\\t\\t    close\\n        }\\n        temporaryMessage\\n\\t    }\\n\\t    ... on Cafe {\\n        phoneNumber\\n        photo\\n        timezone\\n\\t\\t    hours {\\n\\t\\t\\t    day\\n\\t\\t\\t    open\\n\\t\\t\\t    close\\n        }\\n        temporaryMessage\\n      }\\n          }\\n        }\"}'
        all_atm = session.post("https://api.capitalone.com/locations",headers=headers,data=payload_allatm)
        json_data = all_atm.json()
        for value in json_data['data']['geoSearch']:
            locator_domain = "https://www.capitalone.com/"
            location_name = value['locationName']
            street_address = value['address']['addressLine1']
            city = value['address']['city']
            state = value['address']['stateCode']
            zipp = value['address']['postalCode']
            country_code = "US"
            try:
                phone = value['phoneNumber']
            except:
                phone = "<MISSING>"

            location_type = value['locType']
            # print(location_name,location_type)
            lat = value['latitude']
            lng = value['longitude']
           
            if location_type == "branch":
                hoo = []
                store_number = value['locationId']
                for i in value['lobbyHours']:
                    day = i['day']
                    op = i['open'].replace(" ","")
                    cl = i['close'].replace(" ","")
                    frame = day + ':' + op + ' - ' + cl
                    hoo.append(frame)
                hours_of_operation = ', '.join(hoo)

            elif location_type == "cafe":
                hoo = []
                store_number = value['locationId']
                for i in value['hours']:
                    day = i['day']
                    op = i['open'].replace(" ","")
                    cl = i['close'].replace(" ","")
                    frame = day + ':' + op + ' - ' + cl
                    hoo.append(frame)
                hours_of_operation = ', '.join(hoo)

            else:
                store_number = "<MISSING>"
                hours_of_operation = "<MISSING>"

            result_coords.append((lat,lng))
            store = []
            store.append(locator_domain)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number)
            store.append(phone)
            store.append(location_type)
            store.append(lat)
            store.append(lng)
            store.append(hours_of_operation)
            store.append("<MISSING>")
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            yield store
          

        if len(json_data) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
