import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('gianteagle_com')





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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept': '*/*'
    }

    addresses = []
    base_url = "https://www.gianteagle.com"

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

    isFinish = False
    skip_counter = 0
    while isFinish is False:
        r_locations = session.get(
            "https://www.gianteagle.com/api/sitecore/locations/getlocationlistvm?q=&skip=" + str(skip_counter),
            headers=headers)
        json_locations = r_locations.json()

        if json_locations["Locations"] is None or json_locations["FuelPriceVMs"] is None:
            break
        logger.info(str(skip_counter) + " json_locations == " + str(len(json_locations["Locations"])) + " = " + str(
            len(json_locations["FuelPriceVMs"])))
        skip_counter += len(json_locations["Locations"])

        for location_super_market in json_locations["Locations"]:
            store_number = location_super_market["MWGStoreId"]
            location_name = location_super_market["Name"]
            street_address = location_super_market["Address"]["lineOne"]
            if location_super_market["Address"]["lineTwo"] is not None and location_super_market["Address"][
                "lineTwo"].strip() != "-":
                street_address += ", " + location_super_market["Address"]["lineTwo"]
            city = location_super_market["Address"]["City"]
            state = location_super_market["Address"]["State"]["Abbreviation"]
            zipp = location_super_market["Address"]["Zip"]
            phone = location_super_market["TelephoneNumbers"][0]["DisplayNumber"]
            latitude = str(location_super_market["Address"]["Coordinates"]["Latitude"])
            longitude = str(location_super_market["Address"]["Coordinates"]["Longitude"])
            location_type = location_super_market["Details"]["Type"]["Name"]

            # logger.info(str(location_super_market["Address"]["Coordinates"])+" === " + str(latitude))

            hours_of_operation = ""
            index = 0
            days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
            for time_period in location_super_market["HoursOfOperation"]:
                if time_period["DayNumber"] == index + 1:
                    hours_of_operation += days[index] + " " + time_period["HourDisplay"] + " "
                index += 1

            # logger.info("store_number == "+ hours_of_operation)
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation]

            if str(store[2]) + str(store[-3]) not in addresses:
                addresses.append(str(store[2]) + str(store[-3]))

                store = [x.strip() if x and x else "<MISSING>"
                         for x in store]

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
