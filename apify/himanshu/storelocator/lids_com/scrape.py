import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata



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
    return_main_object = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
    }
    base_url = "https://www.lids.com"
    r = session.get(
        base_url + "/api/stores?lat=40.7226698&long=-73.51818329999999&num=1000000000&shipToStore=false", headers=headers)
    data = r.json()

    for i in range(len(data)):
        store_data = data[i]
        store = []
        store.append("https://www.lids.com")
        store.append(store_data['name'])
        store.append(store_data["address1"] + store_data["address2"]
                     if store_data["address2"] != None else store_data["address1"])
        store.append(store_data['city'])
        store.append(store_data['state'])
        store.append(store_data["zip"])
        store.append("US")
        store.append(store_data["storeId"])
        store.append(store_data["phone"]
                     if store_data["phone"] != "" else "<MISSING>")
        store.append("lids " + store_data["locationType"])
        store.append(store_data["latitude"])
        store.append(store_data["longitude"])
        page_url = store_data['storeUrl']
        if "" == page_url:
            page_url = "<MISSING>"
        hours = ""
        if "monFriOpen" in store_data:
            hours = " monFriOpen " + \
                store_data["monFriOpen"] + " monFriClose " + \
                    store_data["monFriClose"] + " "
        if "satOpen" in store_data and store_data["satOpen"] != "":
            hours = " satOpen " + \
                store_data["satOpen"] + " satClose " + \
                    store_data["satClose"] + " "
        if "sunOpen" in store_data and store_data["sunOpen"] != "":
            hours = " sunOpen " + \
                store_data["sunOpen"] + " sunClose " + \
                    store_data["sunClose"] + " "
        store.append(hours if hours != "" else "<MISSING>")
        store.append(page_url)
        return_main_object.append(store)
        # print(str(return_main_object))
        # print("data===" + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~')
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
