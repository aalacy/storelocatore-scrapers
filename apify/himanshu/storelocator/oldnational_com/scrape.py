# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import http.client
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('oldnational_com')




def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 400
    MAX_DISTANCE = 5000
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    result_coords = []
    while coord:

        location_url = "https://www.oldnational.com/API/Locations.svc/Get/"
        lat = coord[0]
        lng = coord[1]
        hours_of_operation3= ''
        hours_of_operation4=''
        conn = http.client.HTTPSConnection("www.oldnational.com")

        # payload = "{\"Lat\":40.72266940.7226698,\"Lon\":-73.51818329999998,\"UserLat\":40.7226698,\"UserLon\":-73.51818329999998,\"Filters\":[\"BR\",\"ATM\",\"PATM\",\"WM\"]}"
        # payload = "{\"Lat\":"+str(lat)+",\"Lon\":"+str(lng)+",\"Filters\":[\"BR\",\"ATM\",\"PATM\",\"WM\"]}"
        payload = '{\"Lat":'+str(lat)+',\"Lon":'+str(lng)+',\"Limit":2147483646,\"Filters":[\"BR",\"ATM",\"PATM",\"WM"],\"Ranges":[10000],\"Fields":null,"ClosestResultFilters":null,"SortBy":"p2","Source":null}'
        headers = {
            'content-type': "application/json",
            'cache-control': "no-cache",
            'postman-token': "1177446e-d9bf-2fed-c8fd-30625187bc9a"
        }
        conn.request("POST", "/API/Locations.svc/Get/", payload, headers)
        res = conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
        # logger.info(json_data)
        current_results_len = (len(json_data))
        for value in json_data['Locations']:

            base_url = "https://www.oldnational.com/"
            # logger.info(value)
            types = value['LocationType']
            if types=="WM":
                types = "Wealth Management"
            
            elif  types=="BR":
                types = "Branche"
            else:
                types = "ATM"
            location_type = types
            locator_domain = base_url
            location_name = value['Name'].strip()
            page_url = base_url + value['Url'].strip()
            street_address = value['Address'].strip()
            city = value['City'].strip()
            state = value['State'].strip()
            zip = value['Zip']
            country_code = 'US'
            store_number ="<MISSING>"
            phone = value['MainPhone']
            # logger.info(phone)
            if str(phone) == 'None':
                phone = ''
            latitude = value['Lat']
            longitude = value['Lon']
            vb = []
            hours_of_operation =''
            hours_of_operation1 = value['DriveThroughHours']
            hours_of_operation2 = value['LobbyHours']
            if  hours_of_operation1 != None:
                hours_of_operation3 ='DriveThroughHours'+' '+ " ".join(hours_of_operation1)
            
            if  hours_of_operation2 != None:
                hours_of_operation4 = 'LobbyHours'+' '+ " ".join(hours_of_operation2)

            result_coords.append((latitude, longitude))
            if street_address in addresses:
                continue
            addresses.append(street_address)
            store = []
            time = hours_of_operation3+' '+hours_of_operation4
            new_time = time.replace("DriveThroughHours None","").replace("LobbyHours By appointment.","").strip().lstrip()
            
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip if zip else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(new_time if new_time else '<MISSING>')
            store.append(page_url if page_url else '<MISSING>')
            
            #logger.info("data = " + str(store))
            #logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()
            # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
