

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('abercrombie_com')




def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


session = SgRequests()


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': 'application/json, text/javascript, */*; q=0.01',
    }

    addresses = []
    base_url = "https://www.abercrombie.com"

    r = session.get("https://www.abercrombie.com/api/ecomm/a-wd/storelocator/search?country=US&radius=10000",
                    headers=headers)
    json_data = r.json()

    return_main_object = []

    # it will used in store data.
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
    page_url = ""

    # logger.info("soup  ==== " + str(json_data))

    for location in json_data["physicalStores"]:
        # logger.info("location ==== " + str(location))
        location_type = location['physicalStoreAttribute'][7]['value'].replace("ACF","abercrombie and fitch").replace("KID","abercrombie and fitch Kids")
        store_number = location["storeNumber"]
        location_name = location["name"]
        city = location["city"]
        state = location["stateOrProvinceName"]
        zipp = location["postalCode"]
        country_code = location["country"]
        latitude = str(location["latitude"])
        longitude = str(location["longitude"])
        phone = location["telephone"]
        street_address = ", ".join(location["addressLine"])

        hours_of_operation = ""
        index = 0
        days = ["Sunday", "Monday", "Tuesday",
                "Wednesday", "Thursday", "Friday", "Saturday"]
        for time_period in location["physicalStoreAttribute"][-1]["value"].split(","):
            hours_of_operation += days[index] + " " + \
                time_period.replace("|", " - ") + " "
            index += 1
        page_url = "https://www.abercrombie.com/shop/wd/clothing-stores/US/" + \
            "".join(city.split()) + "/" + state + "/" + store_number
        # logger.info("phone === "+ str(hours_of_operation))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        # if str(store[2]) in addresses:
        #     continue
        # addresses.append(store[2])

        # store = [x if x else "<MISSING>" for x in store]
        store = [x.encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]

        # logger.info("data = " + str(store))
        # logger.info(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store
    r = session.get("https://www.abercrombie.com/api/ecomm/a-wd/storelocator/search?country=CA&radius=10000",
                    headers=headers)
    json_data = r.json()
    for location in json_data["physicalStores"]:
        # logger.info("location ==== " + str(location))
        location_type = location['physicalStoreAttribute'][7]['value'].replace("ACF","abercrombie and fitch").replace("KID","abercrombie and fitch Kids")
        store_number = location["storeNumber"]
        location_name = location["name"]
        city = location["city"]
        state = location["stateOrProvinceName"]
        zipp = location["postalCode"]
        country_code = location["country"]
        latitude = str(location["latitude"])
        longitude = str(location["longitude"])
        phone = location["telephone"]
        street_address = ", ".join(location["addressLine"])

        hours_of_operation = ""
        index = 0
        days = ["Sunday", "Monday", "Tuesday",
                "Wednesday", "Thursday", "Friday", "Saturday"]
        for time_period in location["physicalStoreAttribute"][-1]["value"].split(","):
            hours_of_operation += days[index] + " " + \
                time_period.replace("|", " - ") + " "
            index += 1

        page_url = "https://www.abercrombie.com/shop/wd/clothing-stores/CA/" + \
            "".join(city.split()) + "/" + state + "/" + store_number

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        # if store[2] in addresses:
        #     continue
        # addresses.append(store[2])

        # store = [x if x else "<MISSING>" for x in store]
        store = [x.encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]

        # logger.info("data = " + str(store))
        # logger.info(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
