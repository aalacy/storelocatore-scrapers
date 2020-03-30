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
    base_url = "https://lonestarnationalbank.com"
    r = session.get("https://lonestarnationalbank.com/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"location-tab"}):
        address1 = location.find("span",{'class':"address1"}).text
        address2 = location.find("span",{'class':"address2"}).text
        name = location.find("div",{'class':"location-name"}).text
        if location.find("a",{"data-phone":re.compile(" ")}) == None:
            phone = "<MISSING>"
        else:
            phone = location.find("a",{"data-phone":re.compile(" ")})["data-phone"]
        hours = " ".join(list(location.find("div",{'class':"hours"}).stripped_strings))
        store = []
        store.append("https://lonestarnationalbank.com")
        store.append(name)
        store.append(address1)
        store.append(address2.split(",")[0])
        store.append(address2.split(",")[1].split(" ")[-2])
        store.append(address2.split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("lone star national bank")
        store.append(location["data-lat"])
        store.append(location["data-lng"])
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
