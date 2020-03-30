import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import sgzip


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
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
    base_url = "https://www.onewestbank.com"
    r = session.get("https://www.onewestbank.com/handlers/StoreLocationsHandler.ashx?BranchLocationsId=23622321295",headers=headers)
    return_main_object = []
    for location in r.text.split("\n")[1:]:
        location_details = location.split('",')
        for i in range(len(location_details)):
            location_details[i] = location_details[i].replace('"',"")
        store = []
        store.append("https://www.onewestbank.com")
        store.append(location_details[1])
        store.append(location_details[2])
        store.append(location_details[3])
        store.append(location_details[4])
        store.append(location_details[5])
        store.append("US")
        store.append(location_details[0])
        store.append(location_details[9] if location_details[9] != "ATM Only" else "<MISSING>")
        store.append("<MISSING>")
        store.append(location_details[7])
        store.append(location_details[8])
        store.append(" ".join(list(BeautifulSoup(location_details[6],"lxml").stripped_strings)))
        store.append('<MISSING>')
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
