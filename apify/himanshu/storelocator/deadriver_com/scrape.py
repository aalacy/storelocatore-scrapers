import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('deadriver_com')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch()
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 50
    current_results_len = 0 
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'content-type': 'application/json',
    }

    base_url = "https://www.deadriver.com"

    while zip_code:
        # logger.info(zip_code)
        result_coords = []
        location_url = "https://www.deadriver.com/LocationFinder.asmx/GetLocation"
        try:
            r = session.post(location_url, headers=headers, data='{"zipCode":"' + zip_code + '"}')
        except:
            pass
        soup = BeautifulSoup(r.text, "lxml")
        text_data = soup.find("p").text.replace('"[', "[").replace(']"', ']').replace('\\\\\\"',"'").replace('\\','')
        json_data = json.loads(text_data) 
        if json_data["d"]:
            current_results_len = len(json_data["d"])
        else:
            current_results_len = 0
        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = "<MISSING>"
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        if current_results_len > 0:
            for location in json_data["d"]:
                # logger.info(location)
                street_address = location["AddressOne"] + " " + location["AddressTwo"]
                city = location["City"]
                zipp = location["ZipCode"]
                state = location["State"]
                # logger.info(zipp)
                phone = location["PhoneOne"]
                longitude = location["Longitude"]
                latitude = location["Latitude"]
                location_name = (str(city)+" , "+str(state))
                # logger.info(location_name)
                page_url = "<MISSING>"
                result_coords.append((latitude, longitude))
                store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                         store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]
                if store[2] in addresses:
                    continue
                addresses.append(str(store[2]))
                store = [x if x else "<MISSING>" for x in store]
                # logger.info("~~~~~~~~~~~~~~~~`"+str(store))
                yield store

        if current_results_len < MAX_RESULTS:
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
