import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import unicodedata

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = requests.get(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    elif method == "post":
        while True:
            try:
                if data:
                    r = requests.post(url,headers=headers,data=data)
                else:
                    r = requests.post(url,headers=headers)
                return r
                break
            except:
                time.sleep(2)
                request_counter = request_counter + 1
                if request_counter > 10:
                    return None
                    break
    else:
        return None

def parser(location_soup,url):
    street_address = " ".join(list(location_soup.find("span",{'class':"c-address-street-1"}).stripped_strings))
    if location_soup.find("span",{'class':"c-address-street-2"}) != None:
        street_address = street_address + " " +  " ".join(list(location_soup.find("span",{'class':"c-address-street-2"}).stripped_strings))
    if location_soup.find("span",{'class':"LocationName"}):
        name = " ".join(list(location_soup.find("span",{'class':"LocationName"}).stripped_strings))
    else:
        name = " ".join(list(location_soup.find("span",{'id':"location-name"}).stripped_strings))
    if location_soup.find("span",{'class':"c-address-city"}):
        city = location_soup.find("span",{'class':"c-address-city"}).text
    else:
        state = url.split("/")[-2]
    if location_soup.find("abbr",{'class':"c-address-state"}):
        state = location_soup.find("abbr",{'class':"c-address-state"}).text
    else:
        state = url.split("/")[-3].upper()
    store_zip = location_soup.find("span",{'class':"c-address-postal-code"}).text
    if location_soup.find("span",{'itemprop':"telephone"}) == None:
        phone = "<MISSING>"
    else:
        phone = location_soup.find("span",{'itemprop':"telephone"}).text
    country = location_soup.find("abbr",{'itemprop':"addressCountry"}).text.strip()
    hours = " ".join(list(location_soup.find("table",{'class':"c-location-hours-details"}).find("tbody").stripped_strings))
    lat = location_soup.find("meta",{'itemprop':"latitude"})["content"]
    lng = location_soup.find("meta",{'itemprop':"longitude"})["content"]
    store = []
    store.append("https://bestbuy.com")
    store.append(name)
    store.append(street_address)
    store.append(city)
    store.append(state)
    store.append(store_zip)
    store.append(country)
    store.append(url.split("-")[-1].replace(".html","").split('/')[0])
    store.append(phone if phone != "" else "<MISSING>")
    store.append("<MISSING>")
    store.append(lat)
    store.append(lng)
    store.append(hours)
    store.append(url)
    #print(store)
    return store

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://bestbuy.com"
    r = requests.get("https://stores.bestbuy.com/index.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for states in soup.find_all("a",{'class':"c-directory-list-content-item-link"}):
        if states["href"].count("/") == 2:
            #print("https://stores.bestbuy.com/" + states["href"].replace("../",""))
            location_request = requests.get("https://stores.bestbuy.com/" + states["href"].replace("../",""))
            location_soup = BeautifulSoup(location_request.text,"lxml")
            if location_soup.find("h2",text=re.compile("We're sorry. This store is permanently closed.")):
                continue
            store_data = parser(location_soup,"https://stores.bestbuy.com/" + states["href"])
            yield store_data
        else:
            state_request = requests.get("https://stores.bestbuy.com/" + states["href"])
            state_soup = BeautifulSoup(state_request.text,"lxml")
            for city in state_soup.find_all("a",{'class':"c-directory-list-content-item-link"}):
                if city["href"].count("/") == 2:
                    #print("https://stores.bestbuy.com/" + city["href"].replace("../",""))
                    location_request = requests.get("https://stores.bestbuy.com/" + city["href"].replace("../",""))
                    location_soup = BeautifulSoup(location_request.text,"lxml")
                    if location_soup.find("h2",text=re.compile("We're sorry. This store is permanently closed.")):
                        continue
                    store_data = parser(location_soup,"https://stores.bestbuy.com/" + city["href"].replace("../",""))
                    yield store_data
                else:
                    #print("https://stores.bestbuy.com/" + city["href"].replace("../",""))
                    city_request = requests.get("https://stores.bestbuy.com/" + city["href"].replace("../",""))
                    city_soup = BeautifulSoup(city_request.text,"lxml")
                    for location in city_soup.find_all("a",{'class':"Teaser-titleLink"}):
                        #print("https://stores.bestbuy.com/" + location["href"].replace("../",""))
                        location_request = requests.get("https://stores.bestbuy.com/" + location["href"].replace("../",""))
                        location_soup = BeautifulSoup(location_request.text,"lxml")
                        if location_soup.find("h2",text=re.compile("We're sorry. This store is permanently closed.")):
                            continue
                        store_data = parser(location_soup,"https://stores.bestbuy.com/" + location["href"].replace("../",""))
                        yield store_data




def scrape():
    data = fetch_data()
    write_output(data)

scrape()
