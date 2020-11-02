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
    base_url = "https://uptownjungle.com"
    r = session.get("https://uptownjungle.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    table = soup.find("div",{"id":"locations"})
    for location in table.find_all("div",{"class":"wpb_wrapper"}):
        name = location.find("h3").text.strip()
        address = list(location.find("p").stripped_strings)
        url = location.find_all("a")[-1]["href"]
        location_request = session.get(url)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        geo_location = location_soup.find("iframe")['src']
        store = []
        store.append("https://uptownjungle.com")
        store.append(name)
        store.append(address[0])
        if len(address[1].split(",")) < 2:
            store.append(address[1].split(" ")[0])
            store.append(address[1].split(" ")[-2].replace("\u200e",""))
            store.append(address[1].split(" ")[-1])
        else:
            store.append(address[1].split(",")[0])
            store.append(address[1].split(",")[1].split(" ")[-2])
            store.append(address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(address[-1])
        store.append("uptown jungle fun park")
        store.append(geo_location.split("!3d")[1].split("!")[0])
        store.append(geo_location.split("!2d")[1].split("!")[0])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
