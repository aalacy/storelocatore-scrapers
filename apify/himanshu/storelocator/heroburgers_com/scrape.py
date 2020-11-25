# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('heroburgers_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 25
    MAX_DISTANCE = 25
    current_results_len = 0  # need to update with no of count.
    coord = search.next_coord()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    result_coords = []
    location_url = "https://heroburgers.com/wp/wp-admin/admin-ajax.php?action=get_all_stores&lat=&lng="

    r = session.get(location_url, headers=headers)

    json_data = r.json()

    if json_data != 0:
        # json_data = json.loads(r_utf)
        # logger.info("json_Data === " + str(json_data))
        # current_results_len = len(json_data)  # it always need to set total len of record.
        # logger.info("current_results_len === " + str(current_results_len))
        for location in json_data:

            value  = json_data[location]
            base_url = "https://heroburgers.com/"

            locator_domain = base_url
            location_name = value['na'].strip()
            page_url = value['gu'].strip()
            street_address = value['st'].strip()

            city = value['ct'].strip()
            state = value['rg'].strip()
            zip = value['zp']
            country_code = value['co'].strip()
            store_number = value['ID']
            phone = value['te'].strip()

            location_type = ""
            latitude = value['lat']
            longitude = value['lng']
            vb = []
            for i in value['op'].keys():
                vb.append(value['op'][i])


            hours_of_operation = 'Monday: ' +  str(vb[0]) + ' - ' + str(vb[1]) + ' Tuesday: ' +  str(vb[2]) + ' - ' +  str(vb[3]) + ' Wednesday ' +  str(vb[4]) + ' - ' +   str(vb[5]) + ' Thursday ' +  str(vb[6]) + ' - ' +  str(vb[7]) + ' Friday ' +  str(vb[8]) + ' - ' +  str(vb[9]) + ' Saturday ' +  str(vb[10]) + ' - ' +  str(vb[11]) + ' Sunday ' +  str(vb[12]) + ' - ' +  str(vb[13])

            result_coords.append((latitude, longitude))


            if street_address in addresses:
                continue
            addresses.append(street_address)
            store = []
            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip if zip else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')

            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url if page_url else '<MISSING>')
            logger.info("data = " + str(store))
            logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            yield store

            # coord = search.next_coord()
            # break


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
