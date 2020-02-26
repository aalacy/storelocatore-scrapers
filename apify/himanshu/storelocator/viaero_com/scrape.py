import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.viaero.com"
    r = requests.get("https://info.viaero.com/store-directory")
    soup = BeautifulSoup(r.text,"lxml")
    addressess = []
    for location in soup.find_all('a'):
        if 'Visit Store' in location.text:

            link = 'https://info.viaero.com'+location["href"]
            try:
                location_request = requests.get(link)
            except:
                pass
            location_soup = BeautifulSoup(location_request.text,"lxml")
            data = list(location_soup.find_all("span",{"class":"hs_cos_wrapper hs_cos_wrapper_widget hs_cos_wrapper_type_rich_text"})[1].stripped_strings)
            if "@context" in data[-1]:
                del data[-1]
            location_name = data[1]
            street_address = data[2]
            city = data[-2].split(",")[0]
            state = data[-2].split(",")[1].split(" ")[1]
            zipp = data[-2].split(",")[1].split(" ")[2]
            phone = data[-1]
            
            hour=' '.join((list(location_soup.find("table").stripped_strings)))
            location_script = location_soup.find("script",{"type":"application/ld+json"}).text
             
            latitude = location_script.split('"latitude":')[1].split('"longitude":')[0].strip().replace(",","")
            longitude = location_script.split('"longitude":')[1].split('},')[0].strip()
      

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
            store.append(latitude)
            store.append(longitude)
            store.append(hour)
            store.append(link)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            # print(store)
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
