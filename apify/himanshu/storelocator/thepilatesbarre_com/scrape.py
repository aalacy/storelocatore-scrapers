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

    base_url = "http://thepilatesbarre.com"
    r = session.get("http://thepilatesbarre.com/",headers=headers)
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all("div",{"class":"location"}):
        name = location.find("a").text
        address = list(location.find("div",{"itemprop":"address"}).stripped_strings)
        phone = location.find("span",{"itemprop":"telephone"}).text
        geo_location = location.find_all("a")[-2]["href"]
        store = []
        store.append("http://thepilatesbarre.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1])
        store.append(address[-2])
        store.append(address[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("the pilates barre")
        lat = ""
        lng = ""
        if "&ll=" in geo_location:
            lat = geo_location.split("&ll=")[1].split(",")[0]
            lng = geo_location.split("&ll=")[1].split(",")[1].split("&")[0]
        elif "/@" in geo_location:
            lat = geo_location.split("/@")[1].split(",")[0]
            lng = geo_location.split("/@")[1].split(",")[1]
        store.append(lat if lat != "" else "<INACCESSIBLE>")
        store.append(lng if lng != "" else "<INACCESSIBLE>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
