# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
import requests 

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.roundtablepizza.com/"
    r = requests.get("https://orders.roundtablepizza.com/locations", headers=headers)
    soup = BeautifulSoup(r.text, "lxml") 
    for link in soup.find("ul",{'id':'ParticipatingStates'}).find_all("a"):
        state_link = "https://orders.roundtablepizza.com"+link['href']
        city_r = requests.get(state_link)
        city_soup = BeautifulSoup(city_r.text, "lxml")
        for url in city_soup.find("ul",{'id':'ParticipatingRestaurants'}).find_all("a"):
            page_url = url['href']
            location_r = requests.get(page_url)
            location_soup = BeautifulSoup(location_r.text, "lxml")

            location_name = location_soup.find("div",{'class':"fn org"}).text.strip()
            street_address = location_soup.find("span",{"class":"street-address"}).text.strip()
            city = location_soup.find("span",{"class":"locality"}).text.strip()
            state = location_soup.find("span",{"class":"region"}).text.strip()
            zipp = location_soup.find("span",{"class":"postal-code"}).text.strip()
            phone = location_soup.find("span",{"class":"tel"}).text.strip()
            store_number = location_soup.find("script",{"id":"registerVendorAnalytics"}).text.split("'Store Number': '")[1].split("',")[0]
            latitude = location_soup.find("meta", {"property":"og:latitude"})['content']
            longitude = location_soup.find("meta", {"property":"og:longitude"})['content']
            hours = " ".join(list(location_soup.find("dl",{"id":"available-business-hours-popover"}).stripped_strings))

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append(store_number) 
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            yield store

    

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
