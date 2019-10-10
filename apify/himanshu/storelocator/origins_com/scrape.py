import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    }
    data = 'JSONRPC=%5B%7B%22method%22%3A%22locator.doorsandevents%22%2C%22id%22%3A5%2C%22params%22%3A%5B%7B%22fields%22%3A%22DOOR_ID%2C+DOORNAME%2C+EVENT_NAME%2C+EVENT_START_DATE%2C+EVENT_END_DATE%2C+EVENT_IMAGE%2C+EVENT_FEATURES%2C+EVENT_TIMES%2C+SERVICES%2C+STORE_HOURS%2C+ADDRESS%2C+ADDRESS2%2C+STATE_OR_PROVINCE%2C+CITY%2C+REGION%2C+COUNTRY%2C+ZIP_OR_POSTAL%2C+PHONE1%2C+STORE_TYPE%2C+LONGITUDE%2C+LATITUDE%2C+SUB_HEADING%22%2C%22radius%22%3A%2210000000000%22%2C%22country%22%3A%22%22%2C%22region_id%22%3A%220%22%2C%22latitude%22%3A33.755711%2C%22longitude%22%3A-84.3883717%2C%22uom%22%3A%22mile%22%7D%5D%7D%5D'
    r = requests.post("https://www.origins.com/rpc/jsonrpc.tmpl?dbgmethod=locator.doorsandevents",headers=headers,data=data)
    data = r.json()[0]["result"]["value"]["results"]
    return_main_object = []
    for key in data:
        store_data = data[key]
        store = []
        store.append("https://www.origins.com")
        store.append(store_data["DOORNAME"].strip())
        store.append((store_data["ADDRESS"] + " " + store_data["ADDRESS2"]).strip())
        store.append(store_data["CITY"] if store_data["CITY"] != "" else "<MISSING>")
        store.append(store_data["STATE_OR_PROVINCE"] if store_data["STATE_OR_PROVINCE"] != "" else "<MISSING>")
        store.append(store_data["ZIP_OR_POSTAL"] if store_data["ZIP_OR_POSTAL"] != "" else "<MISSING>")
        if store_data["COUNTRY"] == "United States":
            store.append("US")
        elif store_data["COUNTRY"] == "Canada":
            store.append("CA")
        else:
            continue
        if store_data["ZIP_OR_POSTAL"] == "":
            continue
        store.append(key)
        store.append(store_data["PHONE1"] if store_data["PHONE1"] != "" and store_data["PHONE1"] != "TBD" else "<MISSING>")
        store.append("origins")
        store.append(store_data["LATITUDE"])
        store.append(store_data["LONGITUDE"])
        store.append(" ".join(list(BeautifulSoup(store_data["STORE_HOURS"],"lxml").stripped_strings)).replace("\xa0"," ") if store_data["STORE_HOURS"] != "" else "<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
