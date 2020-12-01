import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from datetime import datetime
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('navyfederal_org')




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 25.0
    coord = search.next_coord()
    while coord:
        while True:
            try:
                result_coords = []
                # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
                x = coord[0]
                y = coord[1]
                # logger.info('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
                r = session.get("https://www.navyfederal.org/branches-atms/location_search.php?lat="+ str(x) + "&lon=" + str(y) + "&dist=25&loc=50",headers=headers)
                data = r.json()["coordLocation"]["data"]["locations"]
                for store_data in data:
                    if store_data["country"] != "USA":
                        continue
                    lat = store_data["lat"]
                    lng = store_data["lon"]
                    result_coords.append((lat, lng))
                    store = []
                    store.append("https://www.navyfederal.org")
                    store.append(store_data["name"])
                    store.append(store_data["address"])
                    if store[-1] in addresses:
                        continue
                    addresses.append(store[-1])
                    store.append(store_data["city"]  if "city" in store_data else "<MISSING>")
                    store.append(store_data["state"]  if "state" in store_data else "<MISSING>")
                    store.append(store_data["zipcode"] if "zipcode" in store_data else "<MISSING>")
                    if store[-1].split("-")[0].isdigit() == False:
                        store[-1] = "<MISSING>"
                    store.append("US")
                    store.append("<MISSING>")
                    store.append(store_data["phone"] if "phone" in store_data and store_data["phone"] != "" and store_data["phone"] != None  else "<MISSING>")
                    store.append(store_data["locationType"] if store_data["locationType"] else "<MISSING>")
                    store.append(lat)
                    store.append(lng)
                    hours = ""
                    if 'monopen' in store_data and store_data["monopen"] != None:
                        hours = hours + " monday " + store_data["monopen"] + " - " + store_data["monclose"]
                    if 'tuesopen' in store_data and store_data["tuesopen"] != None:
                        hours = hours + " tuesday " + store_data["tuesopen"] + " - " + store_data["tuesclose"]
                    if 'wedopen' in store_data and store_data["wedopen"] != None:
                        hours = hours + " wednesda " + store_data["wedopen"] + " - " + store_data["wedclose"]
                    if 'thuopen' in store_data and store_data["thuopen"] != None:
                        hours = hours + " thursday " + store_data["thuopen"] + " - " + store_data["thuclose"]
                    if 'friopen' in store_data and store_data["friopen"] != None:
                        hours = hours + " friday " + store_data["friopen"] + " - " + store_data["friclose"]
                    if 'satopen' in store_data and store_data["satopen"] != None:
                        hours = hours + " saturday " + store_data["satopen"] + " - " + store_data["satclose"]
                    if 'sunopen' in store_data and store_data["sunopen"] != None:
                        hours = hours + " sunday " + store_data["sunopen"] + " - " + store_data["satclose"]
                    store.append(hours if hours != "" else "<MISSING>")
                    store.append("<MISSING>")
                    yield store
                if len(data) < MAX_RESULTS:
                    search.max_distance_update(MAX_DISTANCE)
                elif len(data) == MAX_RESULTS:
                    search.max_count_update(result_coords)
                else:
                    raise Exception("expected at most " + str(MAX_RESULTS) + " results")
                coord = search.next_coord()
                break
            except:
                continue

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
