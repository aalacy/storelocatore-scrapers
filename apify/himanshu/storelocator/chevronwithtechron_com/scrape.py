import csv
from sgrequests import SgRequests
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('chevronwithtechron_com')




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
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 50
    MAX_DISTANCE = 35
    coord = search.next_coord()
    while coord:
        result_coords = []
        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        # logger.info('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        try:
            r = session.get("https://www.chevronwithtechron.com/webservices/ws_getChevronTexacoNearMe_r2.aspx?lat=" + str(x) + "&lng=" + str(y) + "&oLat=" + str(x) + "&oLng=" + str(y) + "&brand=chevronTexaco&radius=" + str(MAX_DISTANCE),headers=headers)
            data = r.json()["stations"]
            for store_data in data:
                lat = store_data["lat"]
                lng = store_data["lng"]
                result_coords.append((lat, lng))
                store = []
                store.append("https://www.chevronwithtechron.com")
                store.append(store_data["name"])
                store.append(store_data["address"])
                if store[-1] in addresses:
                    continue
                addresses.append(store[-1])
                store.append(store_data["city"]  if "city" in store_data else "<MISSING>")
                store.append(store_data["state"]  if "state" in store_data else "<MISSING>")
                store.append(store_data["zip"] if "zip" in store_data else "<MISSING>")
                store.append("US")
                store.append(store_data["id"])
                store.append(store_data["phone"].replace(".","") if "phone" in store_data and store_data["phone"] else "<MISSING>")
                store.append("<MISSING>")
                store.append(lat)
                store.append(lng)
                store.append(store_data["hours"] if store_data["hours"] else "<MISSING>")
                store.append("<MISSING>")
                # logger.info(store)
                yield store
            if len(data) < MAX_RESULTS:
                # logger.info("max distance update")
                search.max_distance_update(MAX_DISTANCE)
            elif len(data) == MAX_RESULTS:
                # logger.info("max count update")
                search.max_count_update(result_coords)
            else:
                raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        except:
            pass        
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()