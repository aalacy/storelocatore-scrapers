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
    base_url = "https://vasafitness.com"
    r = requests.get("https://vasafitness.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"marker"}):
        location_request = requests.get(location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("h1",{'class':"enjoy-the-ride"}).text
        address = list(location_soup.find("div",{'class':"loc-address"}).stripped_strings)
        hours = " ".join(list(location_soup.find("div",{'id':"loc-accordion"}).stripped_strings))
        if location_soup.find("a",{'href':re.compile("tel:")}) == None:
            phone = "<MISSING>"
        else:
            phone = location_soup.find("a",{'href':re.compile("tel:")})["href"].replace("tel: ","")
        store = []
        store.append("https://vasafitness.com")
        store.append(name)
        store.append(address[0])
        store.append(address[1].split(",")[-2])
        store.append(address[1].split(",")[-1].split(" ")[-2])
        store.append(address[1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("vasa fitness")
        store.append(location["data-latt"])
        store.append(location["data-lngg"])
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
