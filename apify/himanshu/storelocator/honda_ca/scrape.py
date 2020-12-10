# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('honda_ca')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 50
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.honda.ca"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        location_url = "https://api.honda.ca/dealer/H/Live/dealers/" + str(lat) + "/" + str(
            lng) + "/with-driving-distance"

        r = session.get(location_url, headers=headers)

        # logger.info("location_url ==== " + location_url)

        # r_utf = r.text

        # soup = BeautifulSoup.BeautifulSoup(r.text, "lxml")
        json_data = r.json()
        # json_data = json.loads(r_utf)
        # logger.info("json_Data === " + str(json_data))
        current_results_len = int(len(json_data["Items"]))  # it always need to set total len of record.
        # logger.info("current_results_len === " + str(current_results_len))

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "CA"
        store_number = ""
        phone = ""
        location_type = "honda"
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""

        for location in json_data["Items"]:

            # logger.info("location ==== " + str(location))
            # do your logic.

            store_number = location["Dealer"]["Id"]
            location_name = location["Dealer"]["Name"]
            street_address = location["Dealer"]["Location"]["Address"]
            city = location["Dealer"]["Location"]["City"]["Name"]
            state = location["Dealer"]["Location"]["Province"]["Abbreviation"]
            zipp = location["Dealer"]["Location"]["PostalCode"]["Value"]
            phone = location["Dealer"]["ContactInformation"]["Phones"][0]["Number"]

            hours_of_operation = ""
            dep_object = {0: "Sales", 1: "Parts", 2: "Service"}
            for dept in location["Dealer"]["Departments"]:
                hours_of_operation += " " + dep_object[dept["Name"]]
                for key in dept["Hours"]:
                    if dept["Hours"][key] == "":
                        hours_of_operation += " " + key + " " + "Closed"
                    else:
                        hours_of_operation += " " + key + " " + dept["Hours"][key]

            latitude = location["Dealer"]["Location"]["Coordinate"]["Latitude"]
            longitude = location["Dealer"]["Location"]["Coordinate"]["Longitude"]

            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [x if x else "<MISSING>" for x in store]

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

        # yield store
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
