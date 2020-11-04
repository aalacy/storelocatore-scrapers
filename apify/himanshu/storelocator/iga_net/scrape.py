import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('iga_net')





session = SgRequests()

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


def fetch_data():
    # zips = sgzip.coords_for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    # it will used in store data.
    locator_domain = "https://www.iga.net/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "CA"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    # skip = 0
    # while True:
    #     logger.info(skip)
    r = session.get(
        "https://www.iga.net/api/en/Store/get?Latitude=45.489599&Longitude=-73.585324&Skip=0&Max=500", headers=headers);

    json_data = r.json()
    for x in json_data['Data']:
        locator_domain = "https://www.iga.net/"
        location_name = x['Name']
        hours_of_operation = x['OpeningHours']
        # logger.info(hours_of_operation)
        street_address = x['AddressMain']['Line']
        city = x['AddressMain']['City']
        state = x['AddressMain']['Province']
        zipp = x['AddressMain']['PostalCode']
        phone = x['PhoneNumberHome']['Number']
        latitude = x['Coordinates']['Latitude']
        longitude = x['Coordinates']['Longitude']
        raw_address = x['RawName']
        store_number = x['Number']
        page_url = "https://www.iga.net" + x["StoreDetailPageUrl"]
        r_loc = session.get(page_url, headers=headers)
        soup_loc = BeautifulSoup(r_loc.text, "lxml")
        div = soup_loc.find("div", {"id": "body_0_main_0_PnlOpenHours"})
        if div == None:
            hours_of_operation = "<MISSING>"
        else:

            hours_of_operation = " ".join(
                list(div.stripped_strings)).replace("Open hours", "").strip()
            # logger.info(hours_of_operation)
            # logger.info("~~~~~~~~~~~~~~~~~~~~`")
        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
        # store = ["<MISSING>" if x == "" else x for x in store]
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        # logger.info("data = " + str(store))
        # logger.info(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
