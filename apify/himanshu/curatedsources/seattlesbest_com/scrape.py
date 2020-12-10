import csv
import os
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('seattlesbest_com')



def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

session = requests.Session()
proxy_password = os.environ["PROXY_PASSWORD"]
proxy_url = "http://auto:{}@proxy.apify.com:8000/".format(proxy_password)
proxies = {
    'http': proxy_url,
    'https': proxy_url
}
session.proxies = proxies

def fetch_data():
    return_main_object = []
    addresses = []
    search = sgzip.ClosestNSearch() # TODO: OLD VERSION [sgzip==0.0.55]. UPGRADE IF WORKING ON SCRAPER!
    search.initialize()
    MAX_RESULTS = 100
    MAX_DISTANCE = 10
    current_results_len = 0     # need to update with no of count.
    zip_code = search.next_zip()

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.seattlesbest.com"

    while zip_code:
        result_coords = []

        # logger.info("remaining zipcodes: " + str(search.zipcodes_remaining()))
        # logger.info("zip_code === "+zip_code)

        location_url = "https://productlocator.iriworldwide.com/productlocator/servlet/ProductLocatorEngine?producttype=upc&radius=" + str(
            MAX_DISTANCE) + "&clientid=243&productfamilyid=SBCO&storesperpage=" + str(MAX_RESULTS) + "&zip=" + str(
            zip_code) + "&productid=1291912261&productid=1291900943&productid=1291912645&productid=1291901254&productid=1291901132&productid=1291912231&productid=1291912130&productid=1291901215&productid=1291901223&productid=1291901206&productid=1291901113&productid=1291901156&productid=1291912212&productid=1291912310&productid=1291912211&productid=1291912340"
        try:

            r = session.get(location_url,headers=headers)
        except:
            continue
        # logger.info("location_url ==== "+location_url)

        soup = BeautifulSoup(r.text, "xml")
        
        current_results_len = int(soup.find("STORES",{"COUNT":re.compile("")})["COUNT"])        # it always need to set total len of record.

        locator_domain = base_url
        location_name = ""
        street_address = ""
        city = ""
        state = ""
        zipp = ""
        country_code = "US"
        store_number = ""
        phone = ""
        location_type = "seattlesbest"
        latitude = ""
        longitude = ""
        raw_address = ""
        hours_of_operation = ""
        page_url = ""

        # logger.info(str(current_results_len) + " === soup ==== "+ str(soup))

        for script in soup.find_all("STORE"):

            store_number = script.find("STORE_ID").text
            street_address = script.find("ADDRESS").text
            city = script.find("CITY").text
            zipp = script.find("ZIP").text
            state = script.find("STATE").text
            phone = script.find("PHONE").text
            longitude = script.find("LONGITUDE").text
            latitude = script.find("LATITUDE").text
            location_name = script.find("NAME").text
            # logger.info("storeid == "+ script.find("STORE_ID").text)
            # do your logic.
            ca_zip_list = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', str(zipp))
            us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(zipp))

            country_code = ""
            if ca_zip_list:
                zipp = ca_zip_list[-1]
                country_code = "CA"

            if us_zip_list:
                zipp = us_zip_list[-1]
                country_code = "US"

            result_coords.append((latitude, longitude))

            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
                     store_number, phone, location_type, latitude, longitude, hours_of_operation,page_url]

            if store[2] + store[-3] not in addresses:
                addresses.append(store[2] + store[-3])

                store = [str(x).strip() if x else "<MISSING>" for x in store]
                # logger.info("data = " + str(store))
                # logger.info('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
                yield store

        if current_results_len < MAX_RESULTS:
            # logger.info("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif current_results_len == MAX_RESULTS:
            # logger.info("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        zip_code = search.next_zip()



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
