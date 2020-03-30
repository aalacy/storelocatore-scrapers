import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parser(location_soup):
    street_address = " ".join(list(location_soup.find("span",{'itemprop':"streetAddress"}).stripped_strings)).replace(","," ") 
    name = location_soup.find("span",{'class':"c-address-city"}).text.replace(",","")
    city = location_soup.find("span",{'class':"c-address-city"}).text.replace(",","")
    state = location_soup.find("span",{'class':"c-address-state"}).text
    store_zip = location_soup.find("span",{'class':"c-address-postal-code"}).text
    phone = location_soup.find("span",{'itemprop':"telephone"}).text
    if location_soup.find("div",{'class':"Hours-table"}) == None:
        hours = "<MISSING>"
    else:
        hours = " ".join(list(location_soup.find("div",{'class':"Hours-table"}).stripped_strings))
        if hours.count("Closed") == 7:
            return None
    lat = location_soup.find("meta",{'itemprop':"latitude"})["content"]
    lng = location_soup.find("meta",{'itemprop':"longitude"})["content"]
    store = []
    store.append("https://www.volvocars.com")
    store.append(name)
    store.append(street_address)
    store.append(city)
    store.append(state)
    store.append(store_zip)
    store.append("US")
    store.append("<MISSING>")
    store.append(phone if phone != "" else "<MISSING>")
    store.append("volvo")
    store.append(lat)
    store.append(lng)
    store.append(hours)
    return store

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.volvocars.com"
    r = session.get("https://usdealers.volvocars.com/index.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for states in soup.find_all("a",{'class':"c-directory-list-content-item-link"}):
        if states["href"].count("/") == 2:
            location_request = session.get("https://usdealers.volvocars.com/" + states["href"].replace("../",""))
            location_soup = BeautifulSoup(location_request.text,"lxml")
            store_data = parser(location_soup)
            if store_data:
                return_main_object.append(store_data)
        else:
            state_request = session.get("https://usdealers.volvocars.com/" + states["href"])
            state_soup = BeautifulSoup(state_request.text,"lxml")
            for city in state_soup.find_all("a",{'class':"c-directory-list-content-item-link"}):
                if city["href"].count("/") == 2:
                    location_request = session.get("https://usdealers.volvocars.com/" + city["href"].replace("../",""))
                    location_soup = BeautifulSoup(location_request.text,"lxml")
                    store_data = parser(location_soup)
                    if store_data:
                        return_main_object.append(store_data)
                else:
                    city_request = session.get("https://usdealers.volvocars.com/" + city["href"].replace("../",""))
                    city_soup = BeautifulSoup(city_request.text,"lxml")
                    for location in city_soup.find_all("a",{'class':"Directory-listLink"}):
                        location_request = session.get("https://usdealers.volvocars.com/" + location["href"].replace("../",""))
                        location_soup = BeautifulSoup(location_request.text,"lxml")
                        store_data = parser(location_soup)
                        if store_data:
                            return_main_object.append(store_data)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
