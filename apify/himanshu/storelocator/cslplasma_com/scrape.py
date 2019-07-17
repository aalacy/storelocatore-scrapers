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
    base_url = "https://www.cslplasma.com"
    r = requests.get(base_url + "/locations/search-results-state")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for option in soup.find('select',{"id":"SelectedState"}).find_all("option"):
        if option['value'] == "":
            continue
        print(option['value'])
        body = {"SelectedState": option["value"]}
        location_request = requests.post("https://www.cslplasma.com/locations/search-results-state",data=body)
        lcoation_soup = BeautifulSoup(location_request.text,"lxml")
        for location in lcoation_soup.find_all("div",{"class":"center-search-item"}):
            store = []
            name = location.find("span",{'class':"center-search-item-name"}).text
            location_address = list(location.find("div",{"class":"center-search-item-addr"}).stripped_strings)
            location_hours = list(location.find('div',{"class":"center-search-item-contact"}).stripped_strings)
            phone = ""
            if "Ph" in location_hours:
                phone = location_hours[location_hours.index("Ph")+1]
            link = location.find("a")['href']
            location_geo_request = requests.get(base_url + link)
            location_geo_soup = BeautifulSoup(location_geo_request.text,"lxml")
            if location_geo_soup.find("a",{"class":"center-location-mapthis"}) == None:
                geo_link = ""
            else:
                geo_link = location_geo_soup.find("a",{"class":"center-location-mapthis"})["href"]
            store = []
            store.append("https://www.cslplasma.com")
            store.append(name)
            store.append(location_address[1] if location_address[1] != "Coming soon" else "<MISSING>")
            store.append(location_address[-1].split(",")[0] if location_address[-1].split(",")[0] != "" else "<MISSING>")
            store.append(location_address[-1].split(",")[1].split(" ")[-2])
            store.append(location_address[-1].split(",")[1].split(" ")[-1])
            store.append("US")
            store.append(link.split("/")[-2])
            store.append(phone if phone != "" else "<MISSING>")
            store.append("CSL Plasma")
            if len(geo_link.split("?sll")) > 1:
                store.append(geo_link.split("?sll=")[1].split(",")[0])
                store.append(geo_link.split("?sll=")[1].split(",")[1].split("&")[0])
            else:
                store.append("<MISSING>")
                store.append("<MISSING>")
            store.append(location_hours[-1] if location_hours[-1] != "Contact Info" and location_hours[-1] != "Coming Soon" else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
