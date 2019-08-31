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
    base_url = "https://www.carespot.com"
    r = requests.get(base_url + "/locations")
    return_main_object = []
    soup = BeautifulSoup(r.text,"lxml")
    for location in soup.find_all("div",{"class":"location-content"}):
        name = location.find("span",{'class':"pin--title"}).text
        location_address = list(location.find("div",{'class':"pin--address"}).stripped_strings)
        location_hours = list(location.find("div",{'class':"pin--hours"}).stripped_strings)
        location_phone = location.find("div",{'class':"pin--telephone"}).text
        geo_location = location.find('a',{"target":'blank'})['href']
        store = []
        store.append("https://www.carespot.com")
        store.append(name)
        store.append(location_address[0])
        if len(location_address) == 1:
            store[-1] = location_address[0].split(",")[0]
            store.append("<MISSING>")
            store.append(location_address[0].split(",")[-1].split(" ")[-2])
            store.append(location_address[0].split(",")[-1].split(" ")[-1])
        elif len(location_address) < 4:
            location_address[-1] = location_address[-1].replace("\xa0"," ")
            store.append(location_address[-1].split(",")[0])
            store.append(location_address[-1].split(",")[-1].split(" ")[-2])
            store.append(location_address[-1].split(",")[-1].split(" ")[-1])
        else:
            store.append(location_address[1])
            store.append(location_address[-2])
            store.append(location_address[-1])
        store.append("US")
        location_id = location.find_all("a")[-1]["href"]
        store.append(location_id.split("/")[-2] if location_id.split("/")[-2] != "" else "<MISSING>")
        store.append(location_phone.replace("Â ","") if location_phone != ""  and location_phone != "COMING SOON" else "<MISSING>")
        store.append("care spot")
        store.append(geo_location.split("?q=")[1].split(",")[0])
        store.append(geo_location.split(",")[-1])
        store.append(" ".join(location_hours) if location_hours != [] else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
