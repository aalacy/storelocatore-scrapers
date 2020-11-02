import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('raymondjames_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []

    headers = {'Accept': '* / *',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
               }

    # it will used in store data.
    locator_domain = "https://www.raymondjames.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "raymondjames"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    page = 1
    isFinish = False
    while isFinish is not True:
        params = {'latitude': 40.7958, 'longitude': -73.6513,
                  'radius': 8000, 'location': '11576', 'page': str(page)}
        r = session.get(
            "https://www.raymondjames.com/dotcom/api/searchbranches/?location=11576&radius=8000", headers=headers, params=params)
        # logger.info("json==" + r.text)
        # logger.info(str(page))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        json_data = r.json()

        if page > 371:
            isFinish = True
            break
        else:
            for result in json_data['results']:
                location_name = result['header']
                if result['subHeaders'] == None:
                    location_name = result['header']
                else:
                    location_name1 = result['header']
                    location_name2 = "".join(result['subHeaders'])
                    ln = location_name1, location_name2
                    location_name = " ".join(ln)
                if result['address']['line2'] == None and result['address']['line3'] == None:
                    street_address = result['address']['line1']

                if result['address']['line2'] != None and result['address']['line3'] == None:
                    street1 = result['address']['line1']
                    street2 = "".join(result['address']['line2'])
                    street12 = street1, street2
                    # logger.info(street12)
                    street_address = " ".join(street12)
                    # logger.info(street_address)
                if result['address']['line1'] != None and result['address']['line2'] != None and result['address']['line3']:
                    street1 = result['address']['line1']
                    street2 = result['address']['line2']
                    street3 = result['address']['line3']
                    street123 = street1, street2, street3
                    street_address = " ".join(street123)

                if result['address']['city'] == None:
                    city = "<MISSING>"
                else:
                    city = result['address']['city']
                if result['address']['state'] == None:
                    state = "<MISSING>"
                else:
                    state = result['address']['state']

                if result['address']['zip'] == None:
                    zipp = "<MISSING>"
                else:
                    zipp = result['address']['zip']
                # logger.info(state, zipp)
                if result['address']['latitude'] == None:
                    latitude = "<MISSING>"
                else:
                    latitude = result['address']['latitude']
                if result['address']['longitude'] == None:
                    longitude = "<MISSING>"
                else:
                    longitude = result['address']['longitude']
                if result['phone'] == None:
                    phone = "<MISSING>"
                else:
                    phone = result['phone']

                hours_of_operation = "<MISSING>"
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation]
                store = ["<MISSING>" if x == "" else x for x in store]
                if store[2] in addresses:
                    continue
                addresses.append(store[2])
                # logger.info("data = " + str(store))
                # logger.info(
                #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

                return_main_object.append(store)

        page += 1
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
