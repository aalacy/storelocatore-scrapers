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
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://www.bmw.ca"
    r = session.get("https://www.bmw.ca/en/fastlane/dealer-locator.html#/dlo/CA/en/BMW_BMWM",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    apiUrl = json.loads(soup.find("div",{"class":"dealerLocatorView"})["data-dlo-config"])["dlo"]["apiUrl"]
    api_request = session.get(apiUrl + "/pois?brand=BMW_BMWM&cached=off&callback=angular.callbacks._0&category=BM&country=CA&language=en&lat=0&lng=0&maxResults=700&showAll=true&unit=km")
    location_data = json.loads(api_request.text.split("angular.callbacks._0(")[1].split("})")[0] + "}")["data"]["pois"]
    for store_data in location_data:
        store = []
        store.append("https://www.bmw.ca")
        store.append(store_data["name"])
        store.append(store_data["street"])
        store.append(store_data["city"])
        store.append(store_data["state"])
        store.append(store_data["postalCode"])
        store.append(store_data["countryCode"])
        store.append(store_data["key"])
        store.append(store_data["attributes"]["telephoneAreaCode"])
        store.append("bmw")
        store.append(store_data["lat"])
        store.append(store_data["lng"])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
