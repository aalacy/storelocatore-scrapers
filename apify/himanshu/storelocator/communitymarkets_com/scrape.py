import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('communitymarkets_com')






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
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/json',
    }

    addresses = []
    base_url = "http://www.communitymarkets.com"

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

    r_json = session.get("https://api.freshop.com/1/stores?app_key=community_markets&has_address=true&limit=-1", headers=headers)
    json_data = r_json.json()
    # soup = BeautifulSoup(r.text, "lxml")

    # logger.info("json_data === "+ str(json_data))
    for location in json_data["items"]:

        # logger.info("location === " + str(location))
        street_address = location["address_1"]
        location_name = location["name"]
        city = location["city"]
        state = location["state"]
        zipp = location["postal_code"]
        latitude = str(location["latitude"])
        longitude = str(location["longitude"])
        store_number = str(location["store_number"])
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(location["phone_md"]))
        phone = phone_list[0]
        page_url = location["url"]
        hours_of_operation = location["hours_md"].replace("\n"," ")

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses and "coming soon" not in location_name.lower():
            addresses.append(str(store[1]) + str(store[2]))

            store = [x.strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
