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
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "http://kickskarate.com"
    r = session.get("http://kickskarate.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("a",text=re.compile("Explore Location")):
        location_request = session.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        geo_location = location_soup.find("a",text=re.compile("Get Directions"))["href"]
        name = " ".join(list(location_soup.find("div",{"class":'col-lg-4 col-md-4 col-sm-18 box bg_red location'}).find("h3").stripped_strings))
        phone = location_soup.find("div",{"class":'col-lg-4 col-md-4 col-sm-18 box bg_red location'}).find("a",{'class':"phone"}).text.strip()
        if len(location_soup.find("div",{"class":'col-lg-4 col-md-4 col-sm-18 box bg_red location'}).find_all("p")) == 1:
            address = list(location_soup.find("div",{"class":'col-lg-4 col-md-4 col-sm-18 box bg_red location'}).find("p").stripped_strings)
            for i in range(len(address)):
                if address[i] == phone:
                    address = address[:i]
                    break
        else:
            address = list(location_soup.find("div",{"class":'col-lg-4 col-md-4 col-sm-18 box bg_red location'}).find("p").stripped_strings)
        store = []
        store.append("http://kickskarate.com")
        store.append(name)
        store.append(" ".join(address[:-1]))
        store.append(address[-1].split(",")[0])
        store.append(address[-1].split(",")[1].split(" ")[-2])
        store.append(address[-1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("kicks karate")
        store.append(geo_location.split("/@")[1].split(",")[0])
        store.append(geo_location.split("/@")[1].split(",")[1])
        store.append(" ".join(location_soup.find("div",{'class':"col-lg-4 col-md-4 col-sm-18 box bg_black"}).stripped_strings).split("Tell")[0])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
