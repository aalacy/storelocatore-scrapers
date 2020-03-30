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
    base_url = "https://www.standardbankpa.com"
    r = session.get("https://www.standardbankpa.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_list = soup.find("div",{"class":'entry location-wrapper'}).find_all("div",{"class":"row one-location-new"})
    geo_locations = soup.find("div",{"class":'entry location-wrapper'}).find_all("script")
    for i in range(0,len(location_list)):
        lat = geo_locations[i].text.split("new google.maps.LatLng(")[1].split(",")[0]
        lng = geo_locations[i].text.split("new google.maps.LatLng(")[1].split(",")[1].split(");")[0]
        hours = " ".join(list(location_list[i].find("div",{"class":"large-11 medium-11 small-16 columns"}).find('div').stripped_strings))
        phone = location_list[i].find("a",{"href":re.compile("tel:")}).text
        name = location_list[i].find("h2").text
        address = list(location_list[i].find("p").stripped_strings)
        store = []
        store.append("https://www.standardbankpa.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[0])
        store.append(address[1].split(",")[1].split(" ")[-2])
        store.append(address[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("standard bank")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
