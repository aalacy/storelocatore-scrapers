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
    base_url = "http://leeshoagiehouse.com"
    r = requests.get("http://leeshoagiehouse.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"location col-xs-12 well"}):
        lat = location.find("meta",{'itemprop':"latitude"})["content"]
        lng = location.find("meta",{'itemprop':"longitude"})["content"]
        name = location.find("h3").text.strip()
        street_address = location.find("span",{'itemprop':"streetAddress"}).text.strip()
        city = location.find("span",{'itemprop':"addressLocality"}).text.strip()
        state = location.find("span",{'itemprop':"addressRegion"}).text.strip()
        store_zip = location.find("span",{'itemprop':"postalCode"}).text.strip()
        phone = location.find("span",{'itemprop':"telephone"}).text.strip()
        hours = " ".join(list(location.find_all("div",{'class':'row'})[-1].stripped_strings))
        store = []
        store.append("http://leeshoagiehouse.com")
        store.append(name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(store_zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.replace("LEES",""))
        store.append("lee's hoagie house")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
