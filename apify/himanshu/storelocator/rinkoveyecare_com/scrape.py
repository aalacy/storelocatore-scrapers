# coding=UTF-8

import csv
# import requests
from bs4 import BeautifulSoup as BS
import re
import json
from sgrequests import SgRequests
session = SgRequests()


def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    addressess = []
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.rinkoveyecare.com"

    link_soup = BS(session.get("https://www.clarksoneyecare.com/our-eye-doctors/").text, "lxml")

    for link in link_soup.find("div",{"class":"doctortabs"}).find_all("a"):
        if "https:" in  link['href']:
            page_url = link['href']
        else:
            page_url = "https://www.clarksoneyecare.com/" + link['href']
        

        location_soup = BS(session.get(page_url).text, "lxml")
        try:
            location_name = location_soup.find("h1",{"class":"location-name"}).text.strip()
        except:
            continue
        addr = list(location_soup.find("address",{"id":"prgmStoreAddress"}).stripped_strings)
        
        street_address = " ".join(addr[:-1]).replace(",","").strip()
        
        city = addr[-1].split(",")[0]
        state = addr[-1].split(",")[1].split()[0].strip()
        zipp =  addr[-1].split(",")[1].split()[1].strip()
        
        phone = location_soup.find("div",{"class":"phone-number"}).text.strip()
        
        lat = location_soup.find("div",{"class":"marker"})['data-lat']
        lng = location_soup.find("div",{"class":"marker"})['data-lng']

        hours = ''
        for hr in location_soup.find("div",{"hours"}).find_all("div",{"class":"day d-flex"}):
            hours+= " "+hr.text+" "


        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url)     
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store 
        
       
        
      

        

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
