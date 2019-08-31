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
    base_url = "https://www.tomjames.com"
    r = requests.get("https://www.tomjames.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    usa_part = BeautifulSoup(soup.find("div",{"class":"white-section center"}).prettify().split("<h4")[2],"lxml")
    for location in usa_part.find_all("a"):
        print(location["href"])
        location_request = requests.get(location["href"].strip(),headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        name = location_soup.find("h1").text
        if name == "Our Apologies":
            continue
        address = list(location_soup.find("span",{"itemprop":"address"}).stripped_strings)
        phone = location_soup.find("span",{"itemprop":"telephone"}).text
        store = []
        store.append("https://www.tomjames.com")
        store.append(name)
        store.append(" ".join(address[:-1]))
        store.append(address[-1].split(",")[0])
        store.append(address[-1].split(",")[-1].split(" ")[-2])
        store.append(address[-1].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("tom james")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<MISSING>")
        return_main_object.append(store)
    for location in soup.find_all("div",{"class":"button-link-white white middle"}):
        if "Canada" in location.find("h6").text:

            location_request = requests.get(location.find("a")["href"].strip(),headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            name = location_soup.find("h1").text
            if name == "Our Apologies":
                continue
            address = list(location_soup.find("span",{"itemprop":"address"}).stripped_strings)
            phone = location_soup.find("span",{"itemprop":"telephone"}).text
            store = []
            store.append("https://www.tomjames.com")
            store.append(name)
            store.append(" ".join(address[:-1]))
            store.append(address[-1].split(",")[0])
            store.append(address[-1].split(",")[-1].split(" ")[1])
            store.append(" ".join(address[-1].split(",")[-1].split(" ")[2:]))
            store.append("CA")
            store.append("<MISSING>")
            store.append(phone)
            store.append("tom james")
            store.append("<INACCESSIBLE>")
            store.append("<INACCESSIBLE>")
            store.append("<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
