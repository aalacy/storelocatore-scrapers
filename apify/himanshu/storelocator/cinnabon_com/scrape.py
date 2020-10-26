import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import time


# def request_wrapper(url, method, headers, data=None):
#     request_counter = 0
#     if method == "get":
#         while True:
#             try:
#                 r = session.get(url, headers=headers)
#                 return r
#                 break
#             except:
#                 time.sleep(2)
#                 request_counter = request_counter + 1
#                 if request_counter > 10:
#                     return None
#                     break
#     elif method == "post":
#         while True:
#             try:
#                 if data:
#                     r = session.post(url, headers=headers, data=data)
#                 else:
#                     r = session.post(url, headers=headers)
#                 return r
#                 break
#             except:
#                 time.sleep(2)
#                 request_counter = request_counter + 1
#                 if request_counter > 10:
#                     return None
#                     break
#     else:
#         return None



session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 30
    # current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()
    # coord = search.next_coord()

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data.
    locator_domain = "https://www.cinnabon.com/"
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    hours_of_operation = "<MISSING>"

    while zip_code:
        result_coords = []

        # print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        # time.sleep(5)
        try:
            r = session.get('https://www.cinnabon.com/Location/Map/Get?brand={A019D0E8-A707-40CC-B647-F3A4670AE0AB}&ZipOrCity='+str(zip_code)+'&userfilters=8c753773-7ff5-4f6f-a550-822523cbafad&userfilters=3431a520-d000-46bb-9058-b000edc96867&userfilters=43ba8d22-b606-4d69-8b91-437e5d6264fd', headers=headers)
        except:
            pass
        json_data = r.json()
        current_results_len = json_data['Locations']
        for location_list in json_data['Locations']:
            if location_list['ComingSoon'] == False and "Cinnabon" in location_list['LocationName']:

                country_code = location_list['CountryName']
                location_name = location_list["AlternativeName"]
                phone = location_list['Tel']
                zipp = location_list['PostalCode']
                state = location_list['Region']
                city = location_list['Locality']
                street_address = location_list['StreetAddress']
                location_type = location_list['LocationType']['Name']
                latitude = location_list['Latitude']
                longitude = location_list['Longitude']
                store_number = location_list['StoreNumber']
                page_url = location_list['Website']
                if page_url == None:
                    page_url = "https://www.cinnabon.com/" + \
                        state.lower() + "/" + "-".join(city.lower().split()) + \
                        "/" + "bakery-" + store_number
                hours_of_operation = "Monnday"+" "+str(location_list['Hours']['Monday'])+" "+"Tuesday"+" "+str(location_list['Hours']['Tuesday'])+" "+"Wednesday"+" "+str(location_list['Hours']['Wednesday'])+" "+"Thursday"+" "+str(location_list['Hours']['Thursday'])+" "+"Friday"+" "+str(location_list['Hours']['Friday'])+" "+"Saturday"+" "+str(location_list['Hours']['Saturday'])+" "+"Sunday"+" "+str(location_list['Hours']['Sunday'])


                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                store = [x if x else "<MISSING>" for x in store]
                store = ['<MISSING>' if x == ' ' or x ==
                         None else x for x in store]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])

                # print("data = " + str(store))
                # print(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store
               
        if len(current_results_len) < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        if len(current_results_len) == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        # else:
        #     raise Exception("expected at most " +
        #                     str(MAX_RESULTS) + " results")

        zip_code = search.next_zip()



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
