import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip

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
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url = "http://salonrepublic.com"
    r = requests.get("http://salonrepublic.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for article in soup.find_all("article",{'class':"myportfolio-container minimal-light"}):
        for location in article.find_all("a"):
            location_request = requests.get(location["href"],headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            store_data = json.loads(location_soup.find_all("script",{"type":"application/ld+json"})[-1].text)
            if "address" not in store_data:
                continue
            lat = ""
            lng = ""
            for script in location_soup.find_all("script"):
                if "var mapdata = " in script.text:
                    location_data = json.loads(script.text.split("var mapdata = ")[1].split("};")[0] + "}")["pois"]
                    for geo_location in location_data:
                        if " ".join(BeautifulSoup(geo_location["body"],"lxml").find("p").text.split(" ")[:2]) in store_data["address"]["streetAddress"]:
                            lat = geo_location["point"]["lat"]
                            lng = geo_location["point"]["lng"]
            store = []
            store.append("http://salonrepublic.com")
            store.append(store_data["name"])
            store.append(store_data["address"]["streetAddress"])
            store.append(store_data["address"]["addressLocality"])
            store.append(store_data["address"]["addressRegion"])
            store.append(store_data["address"]["postalCode"])
            store.append("US")
            store.append("<MISSING>")
            phone = ""
            for p in location_soup.find_all("p"):
                if "Call or Text" in p.text:
                    phone = list(p.stripped_strings)[-2].split("Call or Text ")[1].replace("|","")
            store.append(store_data["telephone"] if phone == "" else phone)
            store.append("salon republic")
            store.append(lat if lat != "" else "<MISSING>")
            store.append(lng if lng != "" else "<MISSING>")
            hours = ""
            store.append(" ".join(store_data["openingHours"]) if "openingHours" in store_data else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
