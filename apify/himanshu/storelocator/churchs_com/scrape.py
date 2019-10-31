import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parser(location_soup,url):
    street_address = " ".join(list(location_soup.find("span",{'class':"c-address-street-1"}).stripped_strings))
    if location_soup.find("span",{'class':"c-address-street-2"}) != None:
        street_address = street_address + " " +  " ".join(list(location_soup.find("span",{'class':"c-address-street-2"}).stripped_strings))
    name = "<MISSING>"
    city = location_soup.find("span",{'class':"c-address-city"}).text
    state = location_soup.find("abbr",{'class':"c-address-state"}).text
    store_zip = location_soup.find("span",{'class':"c-address-postal-code"}).text
    if location_soup.find("div",{'itemprop':"telephone"}) == None:
        phone = "<MISSING>"
    else:
        phone = location_soup.find("div",{'itemprop':"telephone"}).text
    hours = " ".join(list(location_soup.find("table",{'class':"c-hours-details"}).stripped_strings))
    lat = location_soup.find("meta",{'itemprop':"latitude"})["content"]
    lng = location_soup.find("meta",{'itemprop':"longitude"})["content"]
    store = []
    store.append("https://churchs.com")
    store.append(name)
    store.append(street_address)
    store.append(city)
    store.append(state)
    store.append(store_zip)
    store.append("US")
    store.append("<MISSING>")
    store.append(phone if phone != "" else "<MISSING>")
    store.append("<MISSING>")
    store.append(lat)
    store.append(lng)
    store.append(hours)
    store.append(url)
    print(store)
    return store

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://mbfinancial.com"
    r = requests.get("https://locations.churchs.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for states in soup.find_all("a",{'class':"Directory-listLink"}):
        state_request = requests.get("https://locations.churchs.com/" + states["href"])
        state_soup = BeautifulSoup(state_request.text,"lxml")
        for city in state_soup.find_all("a",{'class':"Directory-listLink"}):
            print("https://locations.churchs.com/" + city["href"].replace("../",""))
            city_request = requests.get("https://locations.churchs.com/" + city["href"].replace("../",""))
            city_soup = BeautifulSoup(city_request.text,"lxml")
            for location in city_soup.find_all("a",{'class':"Teaser-titleLink"}):
                print("https://locations.churchs.com/" + location["href"].replace("../",""))
                location_request = requests.get("https://locations.churchs.com/" + location["href"].replace("../",""))
                location_soup = BeautifulSoup(location_request.text,"lxml")
                store_data = parser(location_soup,"https://locations.churchs.com/" + location["href"].replace("../",""))
                yield store_data

def scrape():
    data = fetch_data()  
    
    write_output(data)

scrape()
        
