import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bmwusa_com')




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
    MAX_RESULTS = 300
    MAX_DISTANCE = 300
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize(country_codes=['US'])
    zip_code = search.next_zip()
    current_results_len = 0
    adressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        'Content-Type': 'application/json',
        'Referer': 'https://www.bmwusa.com/?bmw=grp:BMWcom:header:nsc-flyout'
    }
    while zip_code:
        result_coords =[]
       # logger.info("zip_code === "+zip_code)
        #logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        
        base_url = "https://www.bmwusa.com"
        r = session.get("https://www.bmwusa.com/api/dealers/" + str(zip_code) + "/500",headers=headers)
        json_data = r.json()["Dealers"]
        current_results_len = (len(json_data))
        for store_data in json_data:
            store = []
            store.append("https://www.bmwusa.com")
            store.append(store_data["DefaultService"]["Name"])
            store.append(store_data["DefaultService"]["Address"])
            store.append(store_data["DefaultService"]["City"])
            store.append(store_data["DefaultService"]["State"])
            store.append(store_data["DefaultService"]["ZipCode"])
            store.append("US")
            store.append(store_data["CenterId"])
            store.append(store_data["DefaultService"]["FormattedPhone"] if store_data["DefaultService"]["FormattedPhone"] != "" and store_data["DefaultService"]["FormattedPhone"] != None else "<MISSING>")
            store.append("bmw")
            store.append(store_data["DefaultService"]["LonLat"]["Lat"])
            store.append(store_data["DefaultService"]["LonLat"]["Lon"])
            hours = " ".join(list(BeautifulSoup(store_data["DefaultService"]["FormattedHours"],"lxml").stripped_strings))
            store.append(hours if hours != "" else "<MISSING>")
            store.append("<MISSING>")
            if store[2] in adressess:
                continue
            adressess.append(store[2])

            # store = [str(x).strip() if x else "<MISSING>" for x in store]
            yield store

        #logger.info(len(json_data))
        if len(json_data) < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif len(json_data) == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        
        zip_code = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
