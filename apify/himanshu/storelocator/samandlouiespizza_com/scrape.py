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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://samandlouiespizza.com"
    r = requests.get("https://samandlouiespizza.com/locations-and-menus/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"column-1_5 column_padding_bottom"}):
        print(location.find("a")["href"])
        location_request = requests.get(location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        phone = list(location_soup.find("div",{'class':'column-1_2 sc_column_item sc_column_item_2 even'}).find("p").stripped_strings)[-1]
        address = list(location_soup.find("div",{'class':'column-1_2 sc_column_item sc_column_item_2 even'}).find_all("p")[1].stripped_strings)[1:-2]
        hours = " ".join(list(location_soup.find("div",{'class':'column-1_2 sc_column_item sc_column_item_2 even'}).find_all("p")[2].stripped_strings))
        geo_location = location_soup.find("div",{'class':'column-1_2 sc_column_item sc_column_item_2 even'}).find_all("p")[1].find("a")["href"]
        store = []
        store.append("https://samandlouiespizza.com")
        store.append(location_soup.find("div",{'class':'column-1_2 sc_column_item sc_column_item_2 even'}).find("h1").text)
        store.append(" ".join(address[0:-1]))
        if len(address[-1].split(",")) == 2:
            store.append(address[-1].split(",")[0])
            store.append(address[-1].split(",")[-1].split(" ")[-2])
            store.append(address[-1].split(",")[-1].split(" ")[-1])
        else:
            store.append(address[-1].split(",")[0])
            store.append(address[-1].split(",")[1])
            store.append(address[-1].split(",")[2])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("sam & louie's")
        store.append(geo_location.split("/@")[1].split(",")[0] if len(geo_location.split("/@")) == 2 else "<MISSING>")
        store.append(geo_location.split("/@")[1].split(",")[1] if len(geo_location.split("/@")) == 2 else "<MISSING>")
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
