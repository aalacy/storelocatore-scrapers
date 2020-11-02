import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


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
    base_url = "http://ninjasushiusa.com"
    r = session.get("http://ninjasushiusa.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []

    for location in soup.find_all('div',{'class':"col-sm-8"}):
        location_details = list(location.stripped_strings)[:-3]
        store = []
        store.append("http://ninjasushiusa.com")
        if "Center (" in location_details[0]:
            location_details.pop(1)
            location_details.pop(1)
        store.append(location_details[0].replace("(","").strip())
        store.append(location_details[1].replace(",","").strip())
        store.append(location_details[2].split(",")[0])
        store.append(location_details[2].split(",")[1].split(" ")[-2])
        store.append(location_details[2].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[3].split(",")[0])
        store.append("<MISSING>")
        if location.find("a",{'href':re.compile("/@")}) != None:
            geo_location = location.find("a",{'href':re.compile("/@")})["href"]
            store.append(geo_location.split("/@")[1].split(",")[0])
            store.append(geo_location.split("/@")[1].split(",")[1])
        else:
            store.append("<MISSING>")
            store.append("<MISSING>")
        store.append(" ".join(location_details[4:]).replace("Hours:","").strip())
        store.append("http://ninjasushiusa.com/locations")
        store = [x.replace("–","-") for x in store]
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
