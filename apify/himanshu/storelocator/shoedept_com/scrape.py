import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('shoedept_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])

        # logger.info("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    zips = sgzip.for_radius(100)
    return_main_object = []
    addresses = []

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',


    }

    # it will used in store data.
    locator_domain = "https://www.shoedept.com/"
    page_url = "<MISSING>"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"

    for zip_code in zips:

        # logger.info("zip_code == " + zip_code)
        r = session.get(
            'https://www.shoeshowmega.com/on/demandware.store/Sites-shoe-show-Site/default/Stores-FindStores?showMap=true&radius=200&postalCode=' + str(zip_code), headers=headers)
        # logger.info('https://www.shoeshowmega.com/on/demandware.store/Sites-shoe-show-Site/default/Stores-FindStores?showMap=true&radius=200&postalCode='+str(zip_code))

        # logger.info("r===" + r.text)
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~")

        try:
            json_data = r.json()
            # logger.info(json_data['stores'])
            # logger.info('~~~~~~~~~~~~~~~~~~')
            if json_data['stores'] != []:
                for x in json_data['stores']:
                    if x['countryCode'] in ["US", "CA"]:
                        store_number = x['ID']
                        # location_name = x['name']
                        if x['address2'] is not None:
                            if len(x['address2'].split()) == 2:
                                street_address = x['address1'] + \
                                    " " + x['address2']
                                location_name = "<MISSING>"
                            else:
                                location_name = x['address1'].strip()
                                street_address = x['address2'].strip()
                        else:
                            street_address = x['address1']
                            location_name = "<MISSING>"
                        #logger.info(location_name + " | "+street_address)
                        city = x['city']

                        state = x['stateCode']
                        ca_zip_list = re.findall(
                            r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(x['postalCode']))
                        us_zip_list = re.findall(re.compile(
                            r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(x['postalCode']))
                        if us_zip_list:
                            country_code = "US"
                            zipp = us_zip_list[0]
                        elif ca_zip_list:
                            country_code = "CA"
                            zipp = ca_zip_list[0]
                        else:
                            continue
                        # logger.info(zipp)
                        latitude = x['latitude']
                        longitude = x['longitude']
                        phone = x['phone']
                        hours_of_operation = x['storeHours'].replace(
                            '<br>', '    ')

                    store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                             store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
                    store = ["<MISSING>" if x == "" or x ==
                             None else x for x in store]
                    # store = [x if x else "<MISSING>" for x in store]
                    # logger.info(store[1:3])

                    if store_number in addresses:
                        continue
                    addresses.append(store_number)

                    # logger.info("data = " + str(store))
                    # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                    return_main_object.append(store)

        except:
            continue
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
