import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36",
    }
    base_url = "https://bxfitness.com"
    r = session.get("https://bxfitness.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    
    for location in soup.find_all("ul",{"class":"sub-menu"})[2].find_all("a"):
        
        location_request = session.get(location["href"],headers=headers)
        location_soup = BeautifulSoup(location_request.text,"lxml")
        
        hours = " ".join(list(location_soup.find("div",{'class':"hours-data"}).stripped_strings))
        address = list(location_soup.find("div",{"class":'club-address'}).stripped_strings)
        
        
        geo_location = location_soup.find_all("iframe")[0]["src"]
       
        name = location_soup.find("h1").text
        
        store = []
        store.append("https://bxfitness.com")
        store.append(name)
        store.append(address[1])
        store.append(address[2].split(",")[0])
        store.append(address[2].split(",")[1].replace("\xa0"," ").split(" ")[-2])
        store.append(address[2].split(",")[1].replace("\xa0"," ").split(" ")[-1])
        store.append("US")
        store.append("<MISSING>")
        store.append(address[-1])
        store.append("<MISSING>")
        store.append(geo_location.split("!3d")[1].split("!")[0])
        store.append(geo_location.split("!2d")[1].split("!")[0])
        store.append(hours)
        store.append(location["href"])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
