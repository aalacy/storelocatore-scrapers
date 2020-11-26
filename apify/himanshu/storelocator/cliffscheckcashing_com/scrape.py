# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cliffscheckcashing_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    # search.initialize()
    search.initialize(include_canadian_fsas=True)  # with canada zip
    MAX_RESULTS = 100
    MAX_DISTANCE = 500
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.cliffscheckcashing.com"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]

        # lat = 32.7557
        # lng = -96.76546
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        location_url = "http://cliffscheckcashing.com/wp-admin/admin-ajax.php?action=store_search&lat=" + str(
            lat) + "&lng=" + str(lng) + "&max_results=" + str(MAX_RESULTS) + "&search_radius=" + str(
            MAX_DISTANCE) + "&autoload=1"
        # logger.info("location_url === " + str(location_url))
        r = session.get(location_url, headers=headers)
        json_data = r.json()

        current_results_len = int(len(json_data))  # it always need to set total len of record.
        # logger.info("current_results_len === " + str(current_results_len))

        for location in json_data:
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

            location_name = location["store"]
            store_number = location["id"]
            street_address = location["address"]
            if location["address2"]:
                street_address += " " + location["address2"]
            city = location["city"]
            state = location["state"]
            zipp = location["zip"]

            if "United States" == location["country"]:
                country_code = "US"
            elif "Canada" == location["country"]:
                country_code = "CA"
            else:
                country_code = ""

            latitude = location["lat"]
            longitude = location["lng"]
            phone = location["phone"]
            hours_of_operation = " ".join(list(BeautifulSoup(location["hours"], "lxml").stripped_strings))

            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            # logger.info(store[2] + " === hours_of_operation === " + str((store[2] not in addresses)))

            if store[2] not in addresses and country_code:
                addresses.append(store[2])

                store = [str(x).strip() if x else "<MISSING>" for x in store]

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
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
