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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://elgringo.com"
    r = session.get("http://elgringo.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"modal fade"}):
        if "Address:" not in location.text or location.find("button",{'class':"btn btn-default"}) == None:
            continue
        location_details = list(location.stripped_strings)
        store = []
        store.append("http://elgringo.com")
        store.append(location_details[1])
        store.append(location_details[3])
        if len(location_details[4].split(",")) == 3:
            store.append(location_details[4].split(",")[0])
            store.append(location_details[4].split(",")[1])
            store.append(location_details[4].split(",")[2])
        else:
            store.append(" ".join(location_details[4].split(" ")[0:-2]))
            store.append(location_details[4].split(" ")[-2])
            store.append(location_details[4].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[5])
        store.append("el gringo")
        geo_location = location.find_all("a")[1]["href"]
        store.append(geo_location.split("/@")[1].split(",")[0] if len(geo_location.split("/@")) == 2 else geo_location.split("&ll=")[1].split(",")[0])
        store.append(geo_location.split("/@")[1].split(",")[1] if len(geo_location.split("/@")) == 2 else geo_location.split("&ll=")[1].split(",")[1].split("&")[0])
        store.append(location_details[6])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
