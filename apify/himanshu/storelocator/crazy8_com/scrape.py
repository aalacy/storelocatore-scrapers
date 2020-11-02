import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('crazy8_com')




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
    logger.info("started")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    return_main_object = []
    r = session.get("https://www.childrensplace.com/us/stores",headers=headers)
    # logger.info(r)
    store_id = r.text.split("storeId=")[1].split("&")[0]
    base_url = "https://crazy8.com"
    for country in ["united states","canada"]:
        r_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
            "accept": "application/json",
            "storeid": store_id,
            "country": country
        }
        r = session.get("https://www.childrensplace.com/api/v2/store/getStoreLocationByCountry",headers=r_headers)
        data = r.json()["PhysicalStore"]
        for store_data in data:
            page_url = "https://www.childrensplace.com/us/store/" + store_data['uniqueID']
            # logger.info(page_url)
            while True:
                try:
                    location_request = session.get(page_url,headers=headers)
                    break
                except:
                    continue
            location_soup = BeautifulSoup(location_request.text,"lxml")
            for script in location_soup.find_all("script"):
                if "window.__PRELOADED_STATE__ = " in script.text:
                    store_data = json.loads(script.text.split("window.__PRELOADED_STATE__ = ")[1].split("};")[0] + "}")["stores"]["currentStore"]["basicInfo"]
                    address = store_data["address"]
                    store = []
                    store.append("https://crazy8.com")
                    store.append(store_data["storeName"])
                    store.append(address["addressLine1"] + " " + address["addressLine2"] if "addressLine2" in address else address["addressLine1"])
                    store.append(address["city"])
                    store.append(address["state"])
                    store.append(address["zipCode"].replace("                                   ",""))
                    store.append(address["country"])
                    store.append(store_data["id"])
                    store.append(store_data["phone"] if store_data["phone"] else "<MISSING>")
                    store.append("<MISSING>")
                    store.append(store_data["coordinates"]["lat"])
                    store.append(store_data["coordinates"]["long"])
                    hours = " ".join(list(location_soup.find("ul",{'class':"store-day-and-time"}).stripped_strings))
                    store.append(hours if hours else "<MISSING>")
                    store.append(page_url)
                    # logger.info(store)
                    yield store
            
def scrape():
    data = fetch_data()
    write_output(data)

scrape()