import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.savers.com"
    r = session.get("https://maps.savers.com/api/getAsyncLocations?template=search&level=search&radius=1000000000&search=11756",headers=headers)
    return_main_object = []
    location_list = r.json()["markers"]
    for store_data in location_list:
        store_details = list(BeautifulSoup(store_data["info"],"lxml").stripped_strings)
        if len(store_details[2].split(",")) != 2:
            store_details[1] = " ".join(store_details[1:3])
            del store_details[2]
        store = []
        store.append("https://www.savers.com")
        store.append(store_details[0])
        store.append(store_details[1])
        store.append(store_details[2].split(",")[0])
        store.append(store_details[2].split(",")[1].split(" ")[1])
        if len(store_details[2].split(",")[1].split(" ")[-1]) == 3 or len(store_details[2].split(",")[1].split(" ")[-1]) == 6:
            store.append(" ".join(store_details[2].split(",")[1].split(" ")[2:]) if len(" ".join(store_details[2].split(",")[1].split(" ")[2:])) != 6 else " ".join(store_details[2].split(",")[1].split(" ")[2:])[0:3] + " " + " ".join(store_details[2].split(",")[1].split(" ")[2:])[3:])
            store.append("CA")
        else:
            store.append(store_details[2].split(",")[1].split(" ")[-1])
            store.append("US")
        store.append(store_data["locationId"])
        store.append(store_details[3] if store_details[3] != "Distance:" else "<MISSING>" )
        store.append("savers")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        location_request = session.get(BeautifulSoup(store_data["info"],"lxml").find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        store.append(" ".join(list(location_soup.find('div',{'class':"hours"}).stripped_strings)))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
