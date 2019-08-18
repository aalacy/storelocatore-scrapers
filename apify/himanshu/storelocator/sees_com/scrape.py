import csv
import requests
from bs4 import BeautifulSoup
import re
import json

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
    base_url = "https://www.sees.com"
    r = requests.get("https://chocolateshops.sees.com/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for state in soup.find("li",{'class':"rls_countryList rls_US"}).find_all("a"):
        state_request = requests.get(state["href"],headers=headers)
        state_soup = BeautifulSoup(state_request.text,"lxml")
        for city in state_soup.find("div",{'class':"map-list"}).find_all("a"):
            city_request = requests.get(city["href"],headers=headers)
            city_soup = BeautifulSoup(city_request.text,"lxml")
            for location in city_soup.find_all("a",{"class":"store-info"}):
                location_request = requests.get(location["href"],headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                location_details = json.loads(location_soup.find("script",{'type':"application/ld+json"}).text)[0]
                store = []
                store.append("https://www.sees.com")
                store.append(location_details["name"])
                store.append(location_details["address"]["streetAddress"])
                store.append(location_details["address"]["addressLocality"])
                store.append(location_details["address"]["addressRegion"])
                store.append(location_details["address"]["postalCode"])
                store.append("US")
                store.append("<MISSING>")
                store.append(location_details["address"]["telephone"])
                store.append("sees")
                store.append(location_details["geo"]["latitude"])
                store.append(location_details["geo"]["longitude"])
                store.append(location_details["openingHours"])
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
