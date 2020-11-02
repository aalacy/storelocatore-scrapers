import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kindercare_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Content-Type': 'application/json; charset=utf-8'

    }

    # it will used in store data.
    locator_domain = "https://www.kindercare.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "kindercare"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for zip_code in zips:
        r = session.get(
            "https://www.kindercare.com/data/center-search?location=" + str(zip_code) + "&distance=100&edpId=", headers=headers)
        # logger.info("json==" + r.text)
        try:
            json_data = r.json()
        except:
            continue
        # logger.info(json_data)
        if json_data['centers'] == []:
            continue
        else:
            for address_list in json_data['centers']:
                # logger.info(address_list)
                location_name = address_list['name']
                street_address = address_list['address']
                city = address_list['city']
                state = address_list['state']
                zipp = address_list['zip']
                latitude = address_list['latitude']
                longitude = address_list['longitude']
                phone = address_list['phoneNumber']
                hours_of_operation = address_list['openHours'].split(">")[
                    1].split("</")[0]
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]
                if store[2] in addresses:
                    continue
                addresses.append(store[2])

                
                return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
