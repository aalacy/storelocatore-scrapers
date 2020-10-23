import csv
import time

from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('definebody_com')


 



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
    }

    base_url = "https://www.definebody.com"
    addresses = []

    r = session.get("https://definebody.com/fitness-studios/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    for script in soup.find("div", {"id": "locations"}).find_all("a"):

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
        page_url = script["href"]
        # page_url = "http://dubai.definebody.com"
        # logger.info("script === " + str(script["href"]))
        r_location = session.get(page_url, headers=headers)
        soup_location = BeautifulSoup(r_location.text, "lxml")

        full_address = list(soup_location.find("div", {"id": "contact"}).stripped_strings)
        # logger.info("street_address === " + str(full_address))

        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(full_address))
        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address))
        state_list = re.findall(r' ([A-Z]{2}) ', str(full_address))

        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"
        elif us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"
        else:
            zipp = ""
            country_code = ""

        if state_list:
            state = state_list[-1]

        if phone_list:
            phone = phone_list[-1]

        address_index = [i for i, s in enumerate(full_address) if zipp and state in s]

        if address_index and len(address_index)>0:
            city = full_address[address_index[0]].replace(zipp,"").replace(state,"").replace(",","").strip().split(" ")[-1]
            street_address = full_address[address_index[0]].replace(zipp,"").replace(state,"").replace(city,"").replace(",","").strip()
            location_name = full_address[address_index[0]-1].replace("DEFINE:","").strip()
            # logger.info(str(address_index)+" == address_index === "+ str(len(street_address)))

            if street_address == "":
                street_address = full_address[address_index[0]-1]
                location_name = full_address[address_index[0]-2].replace("DEFINE:","").strip()

        latitude = soup_location.find("div",{"class":"et_pb_map"})["data-center-lat"]
        longitude = soup_location.find("div",{"class":"et_pb_map"})["data-center-lng"]
        hours_of_operation = "<INACCESSIBLE>"
        # city = city_state_zipp.replace(zipp, "").replace(state, "").replace(",", "")

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[2]) not in addresses and country_code:
            addresses.append(str(store[2]))

            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
