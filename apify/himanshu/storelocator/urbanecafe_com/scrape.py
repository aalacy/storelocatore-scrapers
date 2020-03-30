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
    base_url = "http://urbanecafe.com"
    r = session.get("http://urbanecafe.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    hours = " ".join(list(soup.find("div",{"id":"hours-widget"}).stripped_strings))
    for location in soup.find_all("div",{"class": "location"}):
        name = location["id"]
        location_details = location.find("div",{"class":"one-third-r loc-info"}).find_all("p",recursive=False)
        geo_location = location.find("iframe")['src']
        if "!2d" and "!3d" in geo_location:
            lat = geo_location.split("!3d")[1].split("!")[0]
            lng = geo_location.split("!2d")[1].split("!")[0]
        else:
            lat = geo_location.split("&ll=")[1].split(",")[0]
            lng = geo_location.split("&ll=")[1].split(",")[1].split("&")[0]
        store = []
        store.append("http://urbanecafe.com")
        store.append(name)
        store.append(location_details[0].text)
        store.append(location_details[1].text.split(",")[0])
        store.append(location_details[1].text.split(",")[1].split(" ")[-2])
        store.append(location_details[1].text.split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(location_details[2].text.split("Phone: ")[1] if location_details[2].text.split("Phone: ")[1] != "" else "<MISSING>")
        store.append("urbane cafe")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
