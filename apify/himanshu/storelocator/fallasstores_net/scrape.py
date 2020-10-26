import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fallasstores_net')






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
        'Accept': 'application/json, text/javascript, */*; q=0.01'
    }

    base_url = "https://www.fallasstores.net"
    addresses = []

    r = session.get("https://storerocket.global.ssl.fastly.net/api/user/1vZ4v6y4Qd/locations", headers=headers)
    json_data = r.json()

    for location in json_data["results"]["locations"]:

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

        store_number = location["id"]
        location_type = location["location_type_name"]
        location_name = location["name"]
        street_address = location["address_line_1"]
        if "address_line_2" in location and location["address_line_2"]:
            street_address += " " + location["address_line_2"]
        if street_address == None:
            street_address = location['address'].split(',')[0].strip()


        if location["city"] != None:
            city = location['city']
        else:
            city = location['address'].split(',')[1].strip()
        if location["state"] != None:
            state = location["state"]
            zip = location["postcode"]
        else:
            sz = location['address'].split(',')[2].split()
            # logger.info(sz)
            if len(sz) ==2:
                state = sz[0].strip()
                zip = sz[-1].strip()

            else:
                state = sz[0].strip()
                zip =location['address'].split(',')[-1].strip()
        if len(zip) ==3:
            zipp= "00"+zip
        else:
            zipp = zip

        # logger.info(street_address +"|"+city+"|"+state+"|"+zipp)


        latitude = location["lat"]
        longitude = location["lng"]
        phone = location["phone"]
        hours_of_operation = str(location["hours"]).replace("{","").replace("}","").replace("'","").replace(",","")

        # logger.info("hours_of_operation == " + hours_of_operation)

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
