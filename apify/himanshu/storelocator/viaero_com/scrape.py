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
    base_url = "https://www.viaero.com"
    r = requests.get("https://stores.viaero.com/")
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all("div",{"class":"location"}):
        name = location.find("div",{"class":"location-name"}).text
        link = location.find("a")["href"]
        location_request = requests.get(link)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        address = list(location.find("div",{"class":"c-address"}).stripped_strings)
        phone = location.find("div",{"class":"location-phone"}).find("a").text
        hours = " ".join(list(location_soup.find("table",{"class":"hours lp-param lp-param-hours"}).stripped_strings))
        for script in location_soup.find_all("script"):
            if "var mapCenter = " in script.text:
                lat = script.text.split("{var mapCenter = {lat: ")[1].split(",")[0]
                lng = script.text.split("{var mapCenter = {lat: ")[1].split(", lng: ")[1].split(",")[0]
        store = []
        store.append("https://www.viaero.com")
        store.append(name)
        store.append(" ".join(address[1:-4]))
        store.append(address[-4])
        store.append(address[-2])
        store.append(address[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("viaero wireless")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
