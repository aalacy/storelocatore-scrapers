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
    base_url = "http://www.rosebudrestaurants.com"
    r = requests.get("http://www.rosebudrestaurants.com/our-restaurants/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{'class':"restaurant"}):
        location_request = requests.get(location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        address = location_soup.find_all("iframe")[-1]['src'].split("!2s")[1].split("!")[0].replace("+"," ").replace("%2C",",")
        phone = location_soup.find("p",{'class':"phone"}).text
        hours = " ".join(list(location_soup.find("div",{'class':"hours"}).stripped_strings))
        store = []
        store.append("http://www.rosebudrestaurants.com")
        store.append(address.split(",")[-3])
        store.append(address.split(",")[-3])
        store.append(address.split(",")[-2])
        store.append(address.split(",")[-1].split(" ")[1])
        store.append(address.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("rose bud")
        store.append(location_soup.find_all("iframe")[-1]['src'].split("!3d")[1].split("!")[0])
        store.append(location_soup.find_all("iframe")[-1]['src'].split("!2d")[1].split("!")[0])
        store.append(hours)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
