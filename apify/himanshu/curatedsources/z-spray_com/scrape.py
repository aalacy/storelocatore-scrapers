import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('z-spray_com')




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.z-spray.com/"
    zips = sgzip.for_radius(100)
    addresses= []

    for z in zips:
        r = requests.get("https://asset.exmark.com/ZSpray/mcapi/ZSprayDealers/GetDealersByZip/"+str(z), headers=header)
        try:
            r_json = r.json()
        except:
            pass
        for id,val in enumerate(r_json):
            locator_domain = base_url
            location_name = val['DealerName']
            street_address = val['Address1']
            city = val['City']
            state = val['State']
            zip = val['Zip']
            store_number = '<MISSING>'
            country_code = '<MISSING>'
            phone = val['Phone']
            location_type = 'z-spray'
            latitude = val['Lat']
            longitude = val['Lng']
            hours_of_operation = '<MISSING>'

            if location_name in addresses:
                continue

            addresses.append(location_name)

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
            # logger.info('----demo '+str(store))
            # return_main_object.append(store)
            yield store



    # return return_main_object






def scrape():
    data = fetch_data()

    write_output(data)


scrape()
