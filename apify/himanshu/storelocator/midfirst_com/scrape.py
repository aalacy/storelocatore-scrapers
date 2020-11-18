import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sgselenium import SgSelenium
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('midfirst_com')



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
    driver = SgSelenium().firefox()

    addresses = []
    base_url = "https://www.midfirst.com"

    driver.get('https://www.midfirst.com/locations')

    cookies_list = driver.get_cookies()
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie['name']] = cookie['value']

    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
        ",", ";")  # use for header cookie

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'cookie': cookies_string,
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    r_token = session.get("https://www.midfirst.com/api/Token/get", headers=headers)
    token_for_post = r_token.json()["Token"]
    token_for_cookie = r_token.headers["Set-Cookie"].split(";")[0] + ";"
    # -----------------------------token and cookies----------------------------------------

    driver.get('https://www.midfirst.com/locations')
    cookies_list = driver.get_cookies()
    # logger.info("cookies_list === " + str(cookies_list))
    cookies_json = {}
    for cookie in cookies_list:
        cookies_json[cookie['name']] = cookie['value']

    cookies_string = str(cookies_json).replace("{", "").replace("}", "").replace("'", "").replace(": ", "=").replace(
        ",", ";")  # use for header cookie

    final_cookies_string = cookies_string + ";" + token_for_cookie
    # logger.info("token_for_post === " + token_for_post)
    # logger.info("final_cookies_string === " + final_cookies_string)

    # -----------------------------------------------------------------------------------

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'cookie': final_cookies_string,
        'accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }

    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 150
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    base_url = "https://www.midfirst.com"

    while coord:
        result_coords = []

        lat = coord[0]
        lng = coord[1]
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info('Pulling Lat-Long %s,%s...' % (str(lat), str(lng)))

        r_location = session.post("https://www.midfirst.com/api/Locations", headers=headers,
                                   data="location-banking-center=on&location-atm=on&location-distance=" + str(
                                       MAX_DISTANCE) + "&location-count=" + str(MAX_RESULTS) + "&location-lat=" + str(
                                       lat) + "&location-long=" + str(
                                       lng) + "&__RequestVerificationToken=" + token_for_post)

        # logger.info("r_location === " + r_location.text)

        json_data = r_location.json()

        current_results_len = int(len(json_data["FilteredResults"]))  # it always need to set total len of record.
        # logger.info("current_results_len === " + str(current_results_len))

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
        hours_of_operation = ""

        for location in json_data["FilteredResults"]:

            # logger.info("location ==== " + str(location))
            # do your logic.

            store_number = str(location["Ref"])
            location_name = location["Name"]
            phone = location["PhoneNumber"]
            latitude = str(location["Latitude"])
            longitude = str(location["Longitude"])
            street_address = location["Address1"] + " " + location["Address2"]
            zipp = location["PostalCode"]
            location_type = location["LocationType"]["Name"]
            city = location["City"]["Name"]
            state = location["State"]["Name"]

            hours_of_operation = ""
            for day_hours in location["Schedules"]:
                hours_of_operation += day_hours["DayOfWeek"]["Name"] + " " + day_hours["OpeningTime"] + " - " + \
                                      day_hours["ClosingTime"] + " "

            # logger.info("hours_of_operation === " + hours_of_operation)
            result_coords.append((latitude, longitude))
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [x.strip() if x else "<MISSING>" for x in store]

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
