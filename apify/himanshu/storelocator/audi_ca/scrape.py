import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('audi_ca')





session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.audi.ca"
    r = session.get(
        "https://cache-dealersearch.audi.com/cached/audi-can.json", headers=headers)
    return_main_object = []
    location_data = r.json()["partners"]
    for store_data in location_data:
        store = []
        store.append("https://www.audi.ca")
        store.append(store_data["name"])
        store.append(" ".join(store_data["address"]["display"][:-1]))
        store.append(store_data["address"]["city"])
        store.append(store_data["address"]["region"]
                     if "region" in store_data["address"] else "<MISSING>")
        store.append(store_data["address"]["zipCode"])
        store.append("CA")
        store.append(store_data["vendorId"])
        store.append(store_data["contactDetails"]["phone"]["display"]
                     if store_data["contactDetails"]["phone"]["display"] != "" else "<MISSING>")
        store.append("<MISSING>")
        store.append(store_data["address"]["latitude"])
        store.append(store_data["address"]["longitude"])
        store.append("<MISSING>")
        store.append("https://www.audi.ca/ca/web/en/dealer-search.html")
        store = [str(x).encode('ascii', 'ignore').decode(
            'ascii').strip() if x else "<MISSING>" for x in store]
        # logger.info("data = " + str(store))
        # logger.info(
        #     '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')

        yield store


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
