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
    base_url = "http://www.foreveryogurt.com"
    r = session.get(base_url + "/mapdemonew/fylocation.csv")
    return_main_object = []
    cr = csv.reader(r.text.splitlines(), delimiter=',')
    my_list = list(cr)
    for i in range(1,len(my_list)):
        store_data = my_list[i]
        store = []
        store.append("http://www.foreveryogurt.com")
        store.append(store_data[2])
        store.append(store_data[5])
        store.append(store_data[6].split(",")[0])
        store.append(store_data[6].split(",")[1].strip())
        store.append(store_data[7].split("<")[0])
        if store_data[7].split("<")[0] == "" or len(store_data[7].split("<")[0]) != 5:
            continue
        store.append("US")
        store.append(store_data[-3])
        store.append(store_data[7].split(">")[1] if store_data[7].split(">")[1] != "" else "<MISSING>")
        store.append("forever yogurt")
        store.append(store_data[-5])
        store.append(store_data[-4])
        store.append(store_data[8] if store_data[8] != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
