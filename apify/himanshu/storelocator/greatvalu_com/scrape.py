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
    base_url = "https://www.greatvalu.com"
    r = session.get("https://www.greatvalu.com/stores/store-search-results.html?displayCount=100000&zipcode=18014",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("div",{"id":"store-search-results"}).find("ul").find_all("li",recursive=False):
        store_id = location["data-storeid"]
        name = location.find("h2",{"class":"store-display-name h6"}).text
        address = location.find("p",{"class":"store-address"}).text
        address2 = location.find("p",{"class":"store-city-state-zip"}).text
        hours = " ".join(list(location.find("ul",{"class":"store-regular-hours"}).stripped_strings)[1:])
        phone = location.find('a',{"aria-label":"phone number"}).text
        store = []
        store.append("https://www.greatvalu.com")
        store.append(name)
        store.append(address)
        store.append(address2.split(",")[0])
        store.append(address2.split(",")[1].split(" ")[-2])
        store.append(address2.split(",")[1].split(" ")[-1])
        store.append("US")
        store.append(store_id)
        store.append(phone if phone != "" else "<MISSING>")
        store.append("great valu markets")
        store.append(location["data-storelat"])
        store.append(location["data-storelng"])
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
