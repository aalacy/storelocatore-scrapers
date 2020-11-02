import csv
import time

from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('knightsinn_com')






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
        'accept': 'application/json, text/javascript, */*; q=0.01'
    }

    base_url = "https://www.knightsinn.com"
    addresses = []

    r = session.get("https://www.redlion.com/api/properties/all.js", headers=headers)
    soup_state = BeautifulSoup(r.text, "lxml")
    json_str_ids = r.text.replace("var hotelsData = ", "").replace(";", "")
    json_hotel_data = json.loads(json_str_ids)
    # logger.info("var hotelsData =  === " + str(json_hotel_data))

    str_id_arry = ""
    # id[1]=6596&id[2]=6111&id[0]=186
    list_str_id_data = []
    index = 1
    for num, name in enumerate(json_hotel_data, start=1):
        str_id_arry += "&id[" + str(index) + "]=" + name.split(",")[2]
        if num % 15 == 0:
            list_str_id_data.append(str_id_arry)
            str_id_arry = ""
            index = 0
        index += 1

    for param in list_str_id_data:
        location_url = "https://www.redlion.com/api/hotels?_format=json" + param
        # logger.info("location_url === " + location_url)
        r_locations = session.get(location_url, headers=headers)
        json_locations = r_locations.json()

        for location in json_locations:
            # logger.info("json data === " + str(location))

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

            # do your logic here.
            page_url = location["Path"]
            store_number = location["Id"]
            location_name = location["Name"]
            longitude = location["LatLng"].split("(")[1].split(" ")[0]
            latitude = location["LatLng"].split("(")[1].split(" ")[1].split(")")[0]
            phone = location["Phone"]
            street_address = location["AddressLine1"]
            if location["AddressLine2"]:
                street_address += " "+ location["AddressLine2"]
            state = location["StateProvince"]
            if location["Country"] == "Canada":
                country_code = "CA"
            elif location["Country"] == "United States":
                country_code = "US"
            else:
                continue
            city = location["City"]
            zipp = location["PostalCode"]

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

            if str(store[2]) not in addresses:
                addresses.append(str(store[2]))

                store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
