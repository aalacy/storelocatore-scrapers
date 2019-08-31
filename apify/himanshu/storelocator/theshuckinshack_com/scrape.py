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
    base_url = "http://www.theshuckinshack.com"
    r = requests.get("http://www.theshuckinshack.com/findashack?location=11756&distance=10000000",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("li",{'class':"location-listing"}):
        name = location.find("span",{'class':"name"}).text
        street = location.find("span",{'class':"address"}).text
        city = location.find("span",{'class':"city"}).text
        phone = location.find("p",{'class':"phone"}).text
        state = location.find("span",{'class':"state"}).text
        store_hours = ""
        for hours in location.find_all("div",{"class":'row hours'}):
            store_hours = store_hours + " " + " ".join(list(hours.stripped_strings))
        lat = location.find("div",{'class':"lat"}).text.strip()
        lng = location.find("div",{'class':"lng"}).text.strip()
        location_id = location.find("div",{'class':"locId"}).text.strip()
        store = []
        store.append("http://www.theshuckinshack.com")
        store.append(name)
        store.append(street)
        store.append(city)
        store.append(state)
        store.append("<MISSING>")
        store.append("US")
        store.append(location_id)
        store.append(phone.split("/")[0] if "Contact Us" not in phone else "<MISSING>")
        store.append("shucking' shack")
        store.append(lat)
        store.append(lng)
        store.append(store_hours if store_hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
