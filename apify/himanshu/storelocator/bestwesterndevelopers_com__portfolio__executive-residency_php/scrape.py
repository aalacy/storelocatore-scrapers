import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import sgzip
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bestwesterndevelopers_com__portfolio__executive-residency_php')


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
    coords = sgzip.coords_for_radius(200)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        'Host': "www.bestwestern.com",
        "Referer": "https://www.bestwestern.com/en_US/book/hotel-search.html",
        "X-Requested-With": "XMLHttpRequest",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "Accept: application/json, text/javascript, */*; q=0.01",
    }
    addresses = []
    for cord in coords:
        r = session.get("https://www.bestwestern.com/bin/bestwestern/proxy?gwServiceURL=HOTEL_SEARCH&distance=250&latitude=" + str(cord[0]) + "&longitude=" + str(cord[1]),headers=headers)
        location_list = r.json()
        
        for location in location_list:
            store_data = location["resortSummary"]
            if "Executive Residency" not in store_data["name"]:
                continue
            if store_data["countryCode"] not in ["US","CA"]:
                continue
            store = []
            store.append("https://bestwesterndevelopers.com/portfolio/executive-residency.php")
            store.append(store_data["name"])
            store.append(store_data["address1"] + " " + store_data["address2"] if "address2" in store_data else store_data["address1"])
            if store[-1] in addresses:
                continue
            addresses.append(store[-1])
            store.append(store_data["city"])
            store.append(store_data["state"])
            store.append(store_data["postalCode"])
            store.append(store_data["countryCode"])
            store.append(location["resort"])
            store.append(store_data["phoneNumber"] if store_data["phoneNumber"] else "<MISSING>")
            store.append("<MISSING>")
            store.append(store_data["latitude"])
            store.append(store_data["longitude"])
            store.append("<MISSING>")
            store.append("https://www.bestwestern.com/bin/bestwestern/proxy?gwServiceURL=HOTEL_SEARCH&distance=250&latitude=" + str(cord[0]) + "&longitude=" + str(cord[1]))
            # logger.info(store)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
