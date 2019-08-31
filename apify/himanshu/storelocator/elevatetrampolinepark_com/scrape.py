import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://elevatetrampolinepark.com/"
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for location in soup.find_all("div",{"class":"hover_box"}):
        link = location.find("a")['href']
        location_request = requests.get(link)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        if location_soup.find("h4") == None:
            continue
        name = location_soup.find("h4").text
        if location_soup.find('div',{"class":'textwidget'}) == None:
            continue
        location_address = list(location_soup.find('div',{"class":'textwidget'}).stripped_strings)
        geo_location = location_soup.find("iframe")['src']
        hours = list(location_soup.find_all('div',{"class":"textwidget"})[-1].stripped_strings)
        store = []
        store.append("https://elevatetrampolinepark.com")
        store.append(name)
        store.append(location_address[0])
        store.append(location_address[1].split(",")[0])
        store.append(location_address[1].split(" ")[-2])
        store.append(location_address[1].split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        if "[" in location_address[-1] and "]" in location_address[-1]:
            store.append(location_address[-2])
        else:
            store.append(location_address[-1])
        store.append("elevate trampoline park")
        store.append(geo_location.split("!3d")[1].split("!")[0])
        store.append(geo_location.split("!2d")[1].split("!")[0])
        store.append(" ".join(hours))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
