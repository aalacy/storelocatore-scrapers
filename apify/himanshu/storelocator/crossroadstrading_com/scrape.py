import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
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
    base_url = "https://crossroadstrading.com"
    r = session.get(base_url + "/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object  = []
    links = []
    for link in soup.find_all("a",{"class": "vc_gitem-link vc-zone-link"}):
        links.append(link["href"])
    links = list(dict.fromkeys(links))
    for i in range(len(links)):
        print(links[i])
        location_request = session.get(links[i],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        for script in location_soup.find_all("script"):
            if "google.maps.LatLng" in script.text:
                geo_location = script.text.split("google.maps.LatLng(")[1].split(")")[0]
        print(geo_location)
        name = location_soup.find("h1",{"class":"entry-title"}).text
        location_details = location_soup.find_all("div",{"class":'wpb_content_element'})[0:3]
        location_address = list(location_details[0].stripped_strings)
        phone = list(location_details[1].stripped_strings)
        store_hours = list(location_details[2].stripped_strings)
        store = []
        store.append("https://crossroadstrading.com")
        store.append(name)
        if len(location_address) == 3:
            if len(location_address[2].split(".")) > 1:
                store.append(location_address[2].split(".")[0])
                store.append(location_address[-1].split(".")[1].split(",")[0])
            else:
                store.append(location_address[2].split(",")[0])
                store.append(location_address[-1].split(",")[1])
            store.append(location_address[-1].split(",")[-1].split(" ")[-2])
            store.append(location_address[-1].split(",")[-1].split(" ")[-1])
        else:
            store.append(location_address[2])
            store.append(location_address[-1].split(",")[0])
            if location_address[-1].split(",")[1].split(" ")[-2] == "":
                store.append(location_address[-1].split(",")[1].split(" ")[-3])
            else:
                store.append(location_address[-1].split(",")[1].split(" ")[-2])
            store.append(location_address[-1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[-1] if phone[-1] != "Phone Number" else "<MISSING>")
        store.append("cross roads")
        store.append(geo_location.split(",")[0])
        store.append(geo_location.split(",")[1])
        hours = ""
        hours = hours + " ".join(store_hours)[2:]
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
