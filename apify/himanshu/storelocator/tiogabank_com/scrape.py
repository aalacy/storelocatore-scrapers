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
    base_url = "https://www.tiogabank.com"
    r = session.get("https://www.tiogabank.com/locations-and-hours/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"large-8 medium-8 small-16 columns"}):
        location_details = list(location.find('div',{"class":"row one-location"}).stripped_strings)
        for script in soup.find_all("script"):
            if location_details[0] in script.text:
                if "new google.maps.LatLng(" in script.text:
                    lat = script.text.split("new google.maps.LatLng(")[1].split(",")[0]
                    lng = script.text.split("new google.maps.LatLng(")[1].split(",")[1].split(")")[0]
        store = []
        store.append("https://www.tiogabank.com")
        store.append(location_details[0])
        store.append(location_details[1])
        store.append(location_details[2].split(",")[0])
        store.append(location_details[2].split(",")[1].split(" ")[1])
        store.append(location_details[2].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        phone = ""
        for i in range(len(location_details)):
            if "Phone: " in location_details[i]:
                phone = location_details[i].split("Phone: ")[1].strip()
        store.append(phone if phone != "" else "<MISSING>")
        store.append("tigo state bank office")
        store.append(lat)
        store.append(lng)
        store_hours = ""
        for hours in location.find_all("div",{"class":"medium-16 columns working-hours"}):
            store_hours = store_hours + " " + " ".join(list(hours.stripped_strings))
        store.append(store_hours if store_hours != "" else "<MISSING>")
        return_main_object.append(store)
    for atm in soup.find("tbody",{"class":"row-hover"}).find_all("tr"):
        location_details = list(atm.stripped_strings)
        store = []
        store.append("https://www.tiogabank.com")
        store.append(location_details[0])
        store.append(" ".join(location_details[0:-1]))
        store.append(location_details[-1].split(",")[0])
        store.append(location_details[-1].split(",")[1])
        store.append("<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("tigo state bank atm")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
