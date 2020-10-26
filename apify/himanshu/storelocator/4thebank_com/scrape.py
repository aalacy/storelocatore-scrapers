import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
import unicodedata


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
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
    MAX_RESULTS = 100
    MAX_DISTANCE = 500
    coord = search.next_coord()
    while coord:
        result_coords = []
        #print("remaining zipcodes: " + str(search.zipcodes_remaining()))
        x = coord[0]
        y = coord[1]
        #print('Pulling Lat-Long %s,%s...' % (str(x), str(y)))
        r = session.get("https://www.busey.com/_/api/branches/" + str(x) + "/" + str(y) + "/500",headers=headers)
        data = r.json()["branches"]
        for store_data in data:
            lat = store_data["lat"]
            lng = store_data["long"]
            result_coords.append((lat, lng))
            store = []
            store.append("https://www.busey.com")
            store.append(store_data["name"])
            store.append(store_data["address"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["city"]  if store_data["city"] else "<MISSING>")
            store.append(store_data["state"]  if store_data["state"] else "<MISSING>")
            store.append(store_data["zip"] if store_data["zip"] else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(store_data["phone"] if "phone" in store_data and store_data["phone"] else "<MISSING>")
            store.append("<MISSING>")
            store.append(lat)
            store.append(lng)
            hours = " ".join(list(BeautifulSoup(store_data["description"],"lxml").stripped_strings))
            store.append(hours if hours else "<MISSING>")
            store.append("<MISSING>")
            for i in range(len(store)):
                if type(store[i]) == str:
                    store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            yield store
        if len(data) < MAX_RESULTS:
            #print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(data) == MAX_RESULTS:
            #print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)


scrape()


