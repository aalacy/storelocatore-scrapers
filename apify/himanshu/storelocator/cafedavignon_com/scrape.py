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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.cafedavignon.com"
    r = session.get("https://www.cafedavignon.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"col sqs-col-3 span-3"}):
        location_details = list(location.stripped_strings)
        if location_details == []:
            continue
        store = []
        store.append("https://www.cafedavignon.com")
        store.append(location_details[0])
        store.append(" ".join(location_details[1:2]))
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[3].replace("\xa0"," "))
        store.append("cafe davignon")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(" ".join(location_details[4:]))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
