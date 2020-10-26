import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
# import sgzip
# import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sleepcountry_ca')





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
    locator_domain = "https://www.sleepcountry.ca"
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
    page_url = "<MISSING>"



    r= session.get('https://www.sleepcountry.ca/find-a-store',headers = headers)
    soup = BeautifulSoup(r.text,'lxml')
    script = soup.find_all('script',{'type':'text/javascript'})[-2]
    # logger.info(script)
    script_text = script.text.split('var stores = ')[-1].split(';')[0]
    # logger.info(script_text)
    json_data = json.loads(script_text)
    for x in json_data['items']:
        location_name = x['name']
        street_address = x['address']
        city = x['city']
        zipp = x['zipcode']
        phone = x['phone']
        latitude= x['lat']
        longitude = x['long']
        hours= BeautifulSoup(x['description'],'lxml')
        list_hours = list(hours.table.stripped_strings)
        hours_of_operation = " ".join(list_hours)
        country_code = "CA"





        store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                 store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
        store = ["<MISSING>" if x == "" or x == None or x == "." else x for x in store]

        # logger.info("data = " + str(store))
        # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        return_main_object.append(store)



    return return_main_object




def scrape():
    data = fetch_data()
    write_output(data)


scrape()
