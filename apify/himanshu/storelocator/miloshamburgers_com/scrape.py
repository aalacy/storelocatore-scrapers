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
    base_url = "https://miloshamburgers.com"
    r = session.get("https://miloshamburgers.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("li",{"class":"js-location"}):
        hours = ""
        hours = hours + " Dining Room " + " ".join(list(BeautifulSoup(location["data-dine"],"lxml").stripped_strings)) + " Drive-Thru " + " ".join(list(BeautifulSoup(location["data-drive"],"lxml").stripped_strings))
        store = []
        store.append("https://miloshamburgers.com")
        store.append(location["data-name"])
        if location["data-city"][-1] == " ":
            location["data-city"] = location["data-city"][:-1]
        store.append(location["data-address"])
        store.append(location["data-city"].split(",")[0])
        store.append(location['data-city'].split(",")[-1].split(" ")[-2])
        store.append(location["data-city"].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location["data-phone"])
        store.append("<MISSING>")
        store.append(location["data-lat"])
        store.append(location["data-lng"])
        store.append(hours.replace("\xa0","").replace("–","-"))
        store.append("https://miloshamburgers.com/locations")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
