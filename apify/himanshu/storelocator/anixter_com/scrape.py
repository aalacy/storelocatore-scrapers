import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.anixter.com"
    r = requests.get("https://fusiontables.googleusercontent.com/embedviz?viz=CARD&q=select+*+from+1vpAly2VF-wmZjM8YJD9GD8hzZKkdkCBVu81lI-pb&tmplt=11&cpr=2")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("td"):
        location_details = list(location.find("div",{"style":"height:170px"}).stripped_strings)
        if location.find("a") == None:
            geo_location = ""
        else:
            geo_location = location.find("a")["href"]
        store = []
        store.append("https://www.anixter.com")
        store.append(location_details[0])
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        location_address = ""
        for k in range(1,len(location_details)):
            if location_details[k] == "Solutions":
                break
            location_address = location_address + " " + location_details[k]
        store.append("US")
        store.append("<MISSING>")
        phone = ""
        for k in range(len(location_details)):
            if len(location_details[k].split(":")) == 2:
                phone = location_details[k].split(":")[1]
        store.append(phone.split("|")[0] if phone != "" and phone != " NA" else "<MISSING>")
        store.append("anixer")
        store.append(geo_location.split("/")[-1].split(",")[0] if len(geo_location.split("/")) < 3 and len(geo_location.split("/")[-1].split(",")) > 1 else "<MISSING>")
        store.append(geo_location.split("/")[-1].split(",")[1] if len(geo_location.split("/")) < 3 and len(geo_location.split("/")[-1].split(",")) > 1 else "<MISSING>")
        store.append("<MISSING>")
        store.append(location_address)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
