import csv
import time

from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('thecolumbiabank_com')






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
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'accept': '*/*',
    }

    base_url = "https://www.thecolumbiabank.com"
    addresses = []

    r = session.post("https://www.fultonbank.com/api/Branches/Search", headers=headers,
                      data="QueryModel.SearchTerm=11576&QueryModel.Radius=10000")
    json_data = r.json()
    soup = BeautifulSoup(json_data["branchFlyouts"].replace("\n", "").replace("\r", "").replace('\\"', '"'),
                         "html.parser")

    soup_preview = BeautifulSoup(json_data["branchResults"].replace("\n", "").replace("\r", "").replace('\\"', '"'),
                                 "html.parser")
    # logger.info("soup_state === "+str(json_data["branchFlyouts"].replace("\n","").replace("\r","").replace('\\"','"')))

    for script in soup.find_all("div", {"class": "location-item expanded-locations-item"}):

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

        full_address = script.find("span", {"class": "location-address"}).text.split(",")
        location_name = script.find("span", {"class": "location-name"}).text

        ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(full_address))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(full_address))
        state_list = re.findall(r' ([A-Z]{2}) ', str(full_address))

        if ca_zip_list:
            zipp = ca_zip_list[-1]
            country_code = "CA"

        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"

        if state_list:
            state = state_list[-1]

        if full_address and len(full_address) > 1:
            city = full_address[-2]
            street_address = full_address[0]

        if script.find("span", {"class": "hours-extended"}):
            hours_of_operation = " ".join(list(script.find("span", {"class": "hours-extended"}).stripped_strings))

        if script.find("span", {"class": "location-phone"}):
            phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"),
                                    str(script.find("span", {"class": "location-phone"}).text))
            phone = phone_list[0]

        latitude = str(soup_preview.find("div", {"data-id": script["data-id"]})["data-lat"])
        longitude = str(soup_preview.find("div", {"data-id": script["data-id"]})["data-long"])

        if latitude == "0" or longitude == "0":
            latitude = ""
            longitude = ""

        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]

        if str(store[1]) + str(store[2]) not in addresses:
            addresses.append(str(store[1]) + str(store[2]))

            store = [x.strip() if x else "<MISSING>" for x in store]

            # logger.info("data = " + str(store))
            # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
