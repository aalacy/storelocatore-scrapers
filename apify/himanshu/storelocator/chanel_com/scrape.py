import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip
import unicodedata
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('chanel_com')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    # search = sgzip.ClosestNSearch()
    # search.initialize()
    # MAX_RESULTS = 500
    # MAX_DISTANCE = 50
    coords = sgzip.coords_for_radius(50)
    for coord in coords:
        # result_coords = []
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        # logger.info('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:70.0) Gecko/20100101 Firefox/70.0',
            "X-Requested-With": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        }
        data = r'geocodeResults=%5B%7B%22address_components%22%3A%5B%7B%22long_name%22%3A%22United+States%22%2C%22short_name%22%3A%22US%22%2C%22types%22%3A%5B%22country%22%2C%22political%22%5D%7D%5D%2C%22geometry%22%3A%7B%22location%22%3A%7B%22lat%22%3A'+ str(x) + r'%2C%22lng%22%3A'+ str(y) + r'%7D%2C%22location_type%22%3A%22APPROXIMATE%22%7D%2C%22types%22%3A%5B%22postal_code%22%5D%7D%5D&iframe=true&radius=50.00'
        r = session.post("https://services.chanel.com/en_US/storelocator/getStoreList",headers=headers,data=data)
        data = r.json()["stores"]
        for store_data in data:
            lat = store_data["latitude"]
            lng = store_data["longitude"]
            # result_coords.append((lat, lng))
            store = []
            store.append("https://www.chanel.com")
            store.append(store_data["translations"][0]["name"])
            store.append(store_data["translations"][0]["address1"] + " " + store_data["translations"][0]["address2"] if store_data["translations"][0]["address2"] else store_data["translations"][0]["address1"])
            store.append(store_data["cityname"] if store_data["cityname"] else "<MISSING>")
            store.append(store_data["statename"] if store_data["statename"] else "<MISSING>")
            store.append(store_data["zipcode"] if store_data["zipcode"] else "<MISSING>")
            ca_zip_split = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}',store[-1])
            if ca_zip_split:
                store.append("CA")
            else:
                store.append("US")
            store.append(store_data["id"])
            store.append(store_data["phone"] if store_data["phone"] else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            hours = ""
            for hour in store_data["openinghours"]:
                if hour["opening"]:
                    hours = hours + " " + hour["day"] + " " + hour["opening"]
            store.append(hours if hours else "<MISSING>")
            store.append("<MISSING>")
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.strip() if type(x) == str else x for x in store]
            store = [x if x.replace(" ","") != "NA" else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            # logger.info(store)
            yield store
        # if len(data) < MAX_RESULTS:
        #     # logger.info("max distance update")
        #     search.max_distance_update(MAX_DISTANCE)
        # elif len(data) == MAX_RESULTS:
        #     # logger.info("max count update")
        #     search.max_count_update(result_coords)
        # else:
        #     raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        # coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()