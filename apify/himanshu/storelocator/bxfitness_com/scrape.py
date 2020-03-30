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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "https://bxfitness.com"
    r = session.get("https://bxfitness.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    location_url = []
    for location in soup.find("main").find_all("a"):
        if location["href"] in location_url:
            continue
        location_url.append(location["href"])
        location_request = session.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        hours = " ".join(list(location_soup.find("aside").find_all("div",{'class':"row"},recursive=False)[2].stripped_strings))
        address = list(location_soup.find("div",{"class":'col-xs-12 col-sm-6 col-md-6 col-lg-6 location-address'}).stripped_strings)
        if "(" in address[-1] and ")" in address[-1]:
            phone = address[-1]
        else:
            phone = "<MISSING>"
        geo_location = location_soup.find_all("iframe")[-1]["src"]
        name = location_soup.find("h1").text
        store = []
        store.append("https://bxfitness.com")
        store.append(name)
        store.append(address[1])
        store.append(address[2].split(",")[0])
        store.append(address[2].split(",")[1].replace("\xa0"," ").split(" ")[-2])
        store.append(address[2].split(",")[1].replace("\xa0"," ").split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.replace("BODY ",""))
        store.append("<MISSING>")
        store.append(geo_location.split("!3d")[1].split("!")[0])
        store.append(geo_location.split("!2d")[1].split("!")[0])
        store.append(hours)
        store.append(location["href"])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
