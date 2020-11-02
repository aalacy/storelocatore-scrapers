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
    base_url = "https://newportdental.com"
    r = session.get(base_url + "/providers?prod=1&prod=2&lang=spa&lang=tag&lang=far&lang=ara&lang=chi&lang=vie&lang=other",verify=False)
    soup = BeautifulSoup(r.text,"lxml")
    scripts = soup.find_all("script")
    return_main_object = []
    for location in soup.find_all("div",{"class":"provider-result row"}):
        location_1 = location.find_all("dl",recusive=False)[1]
        location_details = location_1.find_all("dd",recurive=False)
        full_location = []
        for i in range(len(location_details)):
            full_location.append(list(location_details[i].stripped_strings))
        store = []
        store.append("https://newportdental.com")
        store.append(full_location[0][0])
        store.append(full_location[1][0])
        store.append(full_location[1][1].split(",")[0])
        store.append(full_location[1][1].split(",")[1].split(" ")[-2])
        store.append(full_location[1][1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(full_location[2][0])
        store.append("newport dental")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(" ".join(full_location[3]))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
