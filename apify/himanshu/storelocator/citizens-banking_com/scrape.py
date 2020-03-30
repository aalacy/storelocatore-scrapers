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
    base_url = "https://www.citizens-banking.com"
    r = session.get("https://www.citizens-banking.com/Contact/About-Citizens-Bank/Locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"find-us__location"}):
        name = location.find("div",{"class":"find-us__location-name"}).text
        address = list(location.find("div",{"class":"find-us__location-address"}).stripped_strings)
        hours = ""
        for store_hours in location.find_all("div",{"class":"find-us__location-hours"}):
            hours = hours + " " + " ".join(list(store_hours.stripped_strings))
        lat = location.find("div",{"class":"find-us__location-lat"}).text
        lng = location.find("div",{"class":"find-us__location-lng"}).text
        phone = list(location.find("div",{"class":"find-us__location-phone"}).stripped_strings)[0].split("P: ")[1]
        store = []
        store.append("https://www.citizens-banking.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[1].split(" ")[-2])
        store.append(address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("citizens bank")
        store.append(lat)
        store.append(lng)
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
