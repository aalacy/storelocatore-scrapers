import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('curryupnow_com')






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
    # zips = sgzip.coords_for_radius(100)
    # zips = sgzip.for_radius(50)
    return_main_object = []
    addresses = []

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "application/json, text/plain, */*",
        # "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    base_url = "https://www.curryupnow.com/"
    locator_domain = "https://www.curryupnow.com/"
    location_name = ""
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
        'https://api.storepoint.co/v1/15952ca8657a3c/locations?lat=40.7987048&long=-73.6506776&radius=5000', headers=headers).json()
    for loc_list in r['results']['locations']:
        try:
            if "COMING SOON" not in loc_list['name']:
                # logger.info(location_name)
                location_type = loc_list['tags']
                # logger.info(location_type)
                if "mortar and pestle bar" in location_type:
                    location_type = "mortar and pestle bar"
                else:
                    location_type = "restaurant"
                location_name = loc_list['name']
                latitude = loc_list['loc_lat']
                longitude = loc_list['loc_long']
                address = loc_list['streetaddress'].split(',')
                if len(address) == 2:
                    street_address = address[0]
                    city = " ".join(address[-1].split()[:-1])
                    state = "<MISSING>"
                    zipp = address[-1].split()[-1].strip()

                elif len(address) == 3:
                    street_address = address[0].strip()
                    city = address[1].strip()
                    state = " ".join(address[-1].split()[:-1]).strip()
                    zipp = address[-1].split()[-1].strip()
                else:
                    street_address = address[0].strip()
                    city = address[1].strip()
                    state = address[2].strip()
                    zipp = address[-1].strip()
                if "" != loc_list['phone']:
                    phone = loc_list['phone']
                else:
                    phone = "<MISSING>"
                if "" != loc_list['monday']:
                    hours_of_operation = "monday : " + loc_list['monday'] + " tuesday : " + loc_list['tuesday'] + " wednesday : " + loc_list['wednesday'] + \
                        " thursday : " + loc_list['thursday'] + " friday : " + loc_list['friday'] + \
                        " saturday : " + \
                        loc_list['saturday'] + \
                        " sunday : " + loc_list['sunday']
                else:
                    hours_of_operation = "<MISSING>"
                page_url = loc_list['website']

            #             if store_number in addresses:
            #                 continue

            #             addresses.append(store_number)

                store = []
                store.append(locator_domain if locator_domain else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(street_address if street_address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zipp if zipp else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append(store_number if store_number else '<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append(location_type if location_type else '<MISSING>')
                store.append(latitude if latitude else '<MISSING>')
                store.append(longitude if longitude else '<MISSING>')

                store.append(
                    hours_of_operation if hours_of_operation else '<MISSING>')
                store.append(page_url if page_url else '<MISSING>')
                # logger.info("data====" + str(store))
                # logger.info(
                #     "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

                return_main_object.append(store)
        except:
            continue

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
