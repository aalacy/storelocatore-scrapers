import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('theblackdog_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []



    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
        "accept": "application/json, text/javascript, */*; q=0.01",
        # "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.theblackdog.com/"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = ""
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "theblackdog"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    page_url = "<MISSING>"



    r= session.get('https://stores.boldapps.net/front-end/get_surrounding_stores.php?shop=black-dog-4.myshopify.com&latitude=40.7987048&longitude=-73.6506776&max_distance=50&limit=&calc_distance=',headers = headers)
    json_data = r.json()


    for z in json_data['stores']:
        store_number = z['store_id'].strip()
        location_name = z['name'].strip()
        street_address = z['address'] + " "+ z['address2'].strip()
        city=z['city'].strip()
        state = z['prov_state'].strip()
        zipp = z['postal_zip'].strip()
        country_code =z['country'].strip()
        latitude = z['lat'].strip()
        longitude = z['lng'].strip()
        phone = z['phone'].strip()

        hours_of_operation = z['hours'].replace('\r\n'," ").strip().strip()

        page_url = "<MISSING>"



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

        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        # logger.info("data===="+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        return_main_object.append(store)

    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
