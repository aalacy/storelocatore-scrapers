'''
    issue : Docker fail
    resolution :  Website has changed so i have to Re-wrote the scrapper

'''
import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import http.client
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dailysstores_com')



def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize(include_canadian_fsas = True)
    MAX_RESULTS = 50
    MAX_DISTANCE = 500
    current_results_len = 0  # need to update with no of count.
    # zip_code = search.next_zip()
    coord = search.next_coord()


    # headers = {
    #     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
    #     "accept": "application/json, text/javascript, */*; q=0.01",
    #     # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    # }

    # it will used in store data.
    locator_domain = "https://dailysstores.com/"
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
    page_url = "<MISSING>"




    while coord:

        result_coords = []
        isFinish = False
        # while isFinish is not True:
            # logger.info(coord)
            # try:
        conn = http.client.HTTPSConnection("dailys.com")

        payload = ""

        headers = {
            'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
            'accept': "*/*",
            'cache-control': "no-cache",
            'postman-token': "93c2438e-463d-562c-5a7f-b9d5b0a41de2"
            }

        conn.request("GET", "/wp-admin/admin-ajax.php?action=store_search&lat="+str(coord[0])+"&lng="+str(coord[1])+"&max_results=25&search_radius=50&autoload=1", payload, headers)

        res = conn.getresponse()
        data = res.read().decode("utf-8")
        json_data = json.loads(data)
        current_results_len = (len(json_data))
        #logger.info(current_results_len)
        for loc in json_data:
            country = loc['country']
            country_code = "US"
            location_name = loc['store'].replace('&#8217;',"'").replace('&#8211;','-').strip()
            street_address = loc['address'].strip()
            city = loc['city'].strip()
            state = loc['state'].strip()
            zipp = loc['zip'].strip()
            #logger.info(zipp)
            latitude = loc['lat'].strip()
            longitude = loc['lng'].strip()
            phone = loc['phone'].strip()
            if "" != loc['hours']:
                hours_of_operation = loc['hours'].strip()
            else:
                hours_of_operation = "<MISSING>"
            if "" != loc['url']:
                page_url = loc['url'].strip()
            else:
                page_url = "<MISSING>"




            result_coords.append((latitude, longitude))
            if street_address in addresses:
                continue

            addresses.append(street_address)

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
            store.append(page_url if page_url else '<MISSING>')
            #logger.info("data===="+str(store))
           # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            # yield store

            return_main_object.append(store)


            # except:
            #     isFinish = True
            #     continue




        if current_results_len < MAX_RESULTS:
            #logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            #logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")

        coord = search.next_coord()
        # break
    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
