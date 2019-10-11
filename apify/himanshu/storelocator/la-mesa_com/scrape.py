import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://la-mesa.com"
    r = requests.get("https://la-mesa.com/locations/",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    geo_object = {}
    for location in soup.find_all("a",text=re.compile("Learn More")):
        location_request = requests.get(base_url + location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        location_details = list(location_soup.find("div",{"class":"et_pb_blurb_description"}).stripped_strings)
        if "@" in location_details[-1]:
            del location_details[-1]
        if "Fax" in location_details[-1]:
            del location_details[-1]
        phone = location_soup.find_all("a",{"href":re.compile("tel:")})[-1].text
        store = []
        store.append("https://la-mesa.com")
        store.append(location_soup.find("span",{'class':'brown-bg-h1'}).text)
        store.append(location_details[1])
        store.append(location_details[2].split(",")[0])
        store.append(location_details[2].split(",")[-1].split(" ")[-2])
        store.append(location_details[2].split(",")[-1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.replace("Call ",""))
        store.append(location_details[0])
        if location_soup.find("iframe"):
            geo_location = location_soup.find('iframe')["data-wpfc-original-src"]
            store.append(geo_location.split("!3d")[1].split("!")[0])
            store.append(geo_location.split("!2d")[1].split("!")[0])
        elif location_soup.find('div',{"class":"et_pb_map_pin"}):
            geo_location = location_soup.find('div',{"class":"et_pb_map_pin"})
            store.append(geo_location["data-lat"])
            store.append(geo_location["data-lng"])
        else:
            location_data = json.loads(location_soup.find("script",{"type":"application/ld+json"}).text[:-1])
            store.append(location_data["provider"]["geo"]["latitude"])
            store.append(location_data["provider"]["geo"]["longitude"])
        hours = " ".join(list(location_soup.find("h4",text=re.compile("Hours of Operation")).parent.stripped_strings)[1:])
        store.append(hours if hours else "<MISSING>")
        store.append(base_url + location["href"])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
