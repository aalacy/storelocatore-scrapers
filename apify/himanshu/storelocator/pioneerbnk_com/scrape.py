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
    base_url = "https://www.pioneerbnk.com"
    r = requests.get("https://www.pioneerbnk.com/locations-hours/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find("div",{"class":"fusion-builder-row fusion-row"}).find_all("div",recursive=False):
        if location.find("div",{"class":"fusion-text"}) == None:
            continue
        location_details = list(location.find("div",{"class":"fusion-text"}).stripped_strings)
        lat = location.find("script").text.split('"latitude":"')[1].split('"')[0]
        lng = location.find("script").text.split('"longitude":"')[1].split('"')[0]
        store = []
        store.append("https://www.pioneerbnk.com")
        store.append(location_details[0])
        store.append(location_details[0])
        store.append(location_details[1].split(",")[0])
        store.append(location_details[1].split(",")[1].split(" ")[-2])
        store.append(location_details[1].split(",")[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        for i in range(len(location_details)):
            if "Phone:" in location_details[i]:
                phone = location_details[i].split("Phone:")[1].replace(",","").replace(";","")
        hours = ""
        for i in range(len(location_details)):
            if "Hour" in location_details[i]:
                hours = " ".join(location_details[i:])
                break
        store.append(phone)
        store.append("pioneer bank")
        store.append(lat)
        store.append(lng)
        store.append(hours if hours != "" else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
