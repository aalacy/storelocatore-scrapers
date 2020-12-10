import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('louisvuitton_com')





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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'accept': '*/*',
    }

    addresses = []
    base_url = "http://www.louisvuitton.com"

    r = session.get("https://us.louisvuitton.com/eng-us/stores", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

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

    json_str = soup.text.split("allStores=")[1].split("}}]}")[0] + "}}]}"
    json_Data = json.loads(json_str)
    # logger.info("Soup === " + str(json_Data))

    for location in json_Data["stores"]:

        # logger.info(" location ==== "+ str(location))

        latitude = location["latitude"]
        longitude = location["longitude"]
        store_number = location["storeId"]
        location_name = location["name"]
        street_address = location["street"]
        city = location["city"]
        state = location["state"]
        zipp = location["zip"]

        if len(zipp.split(" ")) > 1:
            if zipp.split(" ")[-1].isdigit():
                zipp = location["zip"].split(" ")[-1]
                state = location["zip"].split(" ")[0]

        phone = location["phone"]

        if "United States" == location["country"]:
            country_code = "US"
        elif "Canada" == location["country"]:
            country_code = "CA"
        else:
            continue

        # logger.info("ssssss ===  " + str(location["state"]))
        # logger.info(str(location["zip"])+" == state ==== " + str(zipp))

        page_url = location["url"]
        r_hours = session.get(page_url, headers=headers)
        soup_hours = BeautifulSoup(r_hours.text, "lxml")

        hours_of_operation = " ".join(
            list(soup_hours.find("ul", {"class": "storeDetailed-horaires-content"}).stripped_strings)).replace("/", "-")

        # logger.info("hours ==== " + str(hours_of_operation))

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
