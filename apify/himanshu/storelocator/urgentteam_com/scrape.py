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
    base_url = "https://www.urgentteam.com"
    r = requests.get("https://www.urgentteam.com/location-search?field_geofield_distance%5Bdistance%5D=1000000&field_geofield_distance%5Borigin%5D=11756")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("article",{"class": "location"}):
        if location.find("div",{'class':"location-directions"}).find("a") == None or location.find("div",{"class":"location-hours"}) == None:
            continue
        name = location.find("h2",{"class":"location-title"}).text
        address = location.find("div",{"class":"street-block"}).text
        city = location.find("span",{"class":"locality"}).text
        state = location.find("span",{"class":"state"}).text
        zip_code = location.find("span",{"class":"postal-code"}).text
        hours = list(location.find("div",{"class":"location-hours"}).stripped_strings)
        phone = location.find("div",{"class":"location-phone"}).text
        store = []
        store.append("https://www.urgentteam.com")
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip_code)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone if phone != "" else "<MISSING>")
        store.append("Urgent Team")
        geo_location = location.find("div",{'class':"location-directions"}).find('a')['href']
        store.append(geo_location.split("/@")[1].split(",")[0] if len(geo_location.split("/@")) > 1 else "<INACCESSIBLE>")
        store.append(geo_location.split("/@")[1].split(",")[1] if len(geo_location.split("/@")) > 1 else "<INACCESSIBLE>")
        store.append(" ".join(hours))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
