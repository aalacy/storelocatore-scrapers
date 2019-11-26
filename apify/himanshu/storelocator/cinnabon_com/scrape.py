import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)
def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas = True)
    MAX_RESULTS = 10
    MAX_DISTANCE = 100
    current_results_len = 0  # need to update with no of count.
    zip_code = search.next_zip()
    # coord = search.next_coord()
    result_coords = []

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
    raw_address = ""
    hours_of_operation = "<MISSING>"

    while zip_code:
        result_coords = []

        # isFinish = False
        # while isFinish is not True:
        try:
            r = requests.get('https://www.cinnabon.com/Location/Map/Get?brand={A019D0E8-A707-40CC-B647-F3A4670AE0AB}&ZipOrCity='+str(zip_code)+'&userfilters=8c753773-7ff5-4f6f-a550-822523cbafad&userfilters=3431a520-d000-46bb-9058-b000edc96867&userfilters=43ba8d22-b606-4d69-8b91-437e5d6264fd')
        except:
            continue
        json_data = r.json()
        current_results_len = len(json_data['Locations'])
        for location_list in json_data['Locations']:
            if location_list['ComingSoon'] == False and "Cinnabon" in location_list['LocationName']:

                country_code = location_list['CountryName']
                location_name = "<MISSING>"
                phone = location_list['Tel']
                zipp = location_list['PostalCode']
                #print(zipp)
                state = location_list['Region']
                city = location_list['Locality']
                street_address = location_list['StreetAddress']
                location_type = location_list['LocationName']
                latitude = location_list['Latitude']
                longitude = location_list['Longitude']
                store_number = location_list['StoreNumber']
                page_url = location_list['Website']
                h = []
                if location_list != {}:
                    for day,hours in location_list['Hours'].items():
                        hours_tag = "{} : {}".format(day,hours)
                        h.append(hours_tag)

                    hours_list =  ",".join(",".join(h).split(',')[1:-2]).strip()
                    if "None" in hours_list:
                        hours_of_operation = "<MISSING>"
                    else:
                        hours_of_operation = hours_list
                else:
                    hours_of_operation = "<MISSING>"

                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                # store = [x if x else "<MISSING>" for x in store]
                store = ['<MISSING>' if x == ' ' or x == None else x for x in store]

                if store[2] in addresses:
                    continue
                addresses.append(store[2])


                #print("data = " + str(store))
                #print( '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                return_main_object.append(store)


            # except:
            #     isFinish = True
            #     continue

        # if current_results_len < MAX_RESULTS:
            # print("max distance update")
        #     search.max_distance_update(MAX_DISTANCE)
        # elif current_results_len == MAX_RESULTS:
        #     # print("max count update")
        #     search.max_count_update(result_coords)
        # else:
        #     raise Exception("expected at most " + str(MAX_RESULTS) + " results")

        zip_code = search.next_zip()
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)


scrape()
