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
    base_url = "https://exoticthairestaurant.com"
    r = session.get("https://exoticthairestaurant.com/index-5.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    iframes = soup.find("div",{'class':"block-indent"}).find_all("div",{'class':"map img-polaroid"})
    addresses = soup.find_all("address")
    for i in range(len(addresses)):
        location_details = list(addresses[i].stripped_strings)
        geo_location = iframes[i].find("iframe")["src"]
        store = []
        store.append("https://exoticthairestaurant.com")
        store.append(location_details[0])
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store.append(location_details[1].split(",")[-1].split(" ")[-2])
        store.append(location_details[1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[3])
        store.append("exotic thai")
        store.append(geo_location.split("&sll=")[1].split(",")[0])
        store.append(geo_location.split("&sll=")[1].split(",")[1].split("&")[0])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
