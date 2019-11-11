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
    base_url = "https://www.genisyscu.org"
    r = requests.get("https://www.genisyscu.org/locations",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    links = []
    for location in soup.find("section",{'class':"inside"}).find_all("tr"):
        if location.find("a")["href"] in links:
            continue
        links.append(location.find("a")["href"])
        location_request = requests.get(base_url + location.find("a")["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        for p in location_soup.find("article").find_all("p"):
            if p.find("strong") == None:
                continue
            address = p.text.strip()
            break
        location_details = list(location_soup.find("article").find("table",recursive=False).stripped_strings)
        name = location_soup.find("article").find("h1",recursive=False).text.strip()
        hours = " ".join(location_details[0::2])
        for i in range(len(location_details)):
            if "Phone:" in location_details[i]:
                phone = location_details[i+1].split("x")[0]
                break
        if "." in address.split(",")[-1]:
            address = ",".join(address.split(",")[:-1]) + "," + address.split(",")[-1].replace("."," ")
        store = []
        store.append("https://www.genisyscu.org")
        store.append(name)
        store.append(address.split(",")[0])
        store.append(address.split(",")[1].replace("\xa0",""))
        store.append(address.split(",")[-1].split(" ")[1].replace("\xa0",""))
        store.append(address.split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("genisys credit union")
        geo_lcoation = location_soup.find_all("iframe")[-1]["src"]
        store.append(geo_lcoation.split("!3d")[1].split("!")[0])
        store.append(geo_lcoation.split("!2d")[1].split("!")[0])
        store.append(hours)
        print(store)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
