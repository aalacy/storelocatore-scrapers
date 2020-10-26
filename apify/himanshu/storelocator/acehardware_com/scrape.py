import csv
import sys
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('acehardware_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.acehardware.com"

    addresses = []
    result_coords = []
    locator_domain = base_url
    location_name = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"
    r = session.get(
        "https://www.acehardware.com/store-directory", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    script = soup.find("script", {"id": "data-mz-preload-storeDirectory"})
    json_data = json.loads(script.text)
    for loc in json_data:
        store_number = loc["code"]
        location_name = loc["name"]
        street_address = loc["address"]["address1"]
        city = loc["address"]["cityOrTown"]
        state = loc["address"]["stateOrProvince"]
        zipp = loc["address"]["postalOrZipCode"]
        country_code = loc["address"]["countryCode"]
        phone = loc["formattedPhoneNumber"]
        hours = loc["regularHours"]
        hours_of_operation = ''
        for key, value in hours.items():
            t1 = "".join(value["label"].split("-")[0].strip()[:-2]) + \
                ":" + "".join(value["label"].split("-")[0].strip()[-2:])
            t2 = "".join(value["label"].split("-")[1].strip()[:-2]) + \
                ":" + "".join(value["label"].split("-")[1].strip()[-2:])
            d1 = datetime.strptime(str(t1), "%H:%M")
            t11 = d1.strftime("%I:%M %p")
            d2 = datetime.strptime(str(t2), "%H:%M")
            t22 = d2.strftime("%I:%M %p")
            hours_of_operation += key + ":" + t11 + " - " + t22 + " "
        page_url = "https://www.acehardware.com/store-details/" + \
            str(store_number)
        cr = session.get(page_url, headers=headers)
        cr_soup = BeautifulSoup(cr.text, "lxml")
        try:
            script = cr_soup.find("script", {"id": "data-mz-preload-store"})
            json_data = json.loads(script.text)
            latitude = json_data["Longitude"]
            longitude = json_data["Latitude"]
           # logger.info(latitude, longitude)
        except Exception as e:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            #logger.info(e)
            #logger.info(page_url)
            #logger.info("====================")

        store = [locator_domain, location_name.encode('ascii', 'ignore').decode('ascii').strip(), street_address.encode('ascii', 'ignore').decode('ascii').strip(), city.encode('ascii', 'ignore').decode('ascii').strip(), state.encode('ascii', 'ignore').decode('ascii').strip(), zipp.encode('ascii', 'ignore').decode('ascii').strip(), country_code,
                 store_number, phone.encode('ascii', 'ignore').decode('ascii').strip(), location_type, latitude, longitude, hours_of_operation.replace("hours", "").encode('ascii', 'ignore').decode('ascii').strip(), page_url]

        # if str(store[2]) + str(store[-3]) not in addresses:
        #     addresses.append(str(store[2]) + str(store[-3]))
        store = [x if x else "<MISSING>" for x in store]
        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
