import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time


session = SgRequests()

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
    name = " ".join(list(location_soup.find("h1",{'id':"location-name"}).stripped_strings))
    city = location_soup.find("span",{'class':"c-address-city"}).text
    state = location_soup.find("abbr",{'class':"c-address-state"}).text
    store_zip = location_soup.find("span",{'class':"c-address-postal-code"}).text
    if location_soup.find("span",{'itemprop':"telephone"}) == None:
        phone = "<MISSING>"
    else:
        phone = location_soup.find("span",{'itemprop':"telephone"}).text
    hours = " ".join(list(location_soup.find("table",{'class':"c-location-hours-details"}).stripped_strings))
    lat = location_soup.find("meta",{'itemprop':"latitude"})["content"]
    lng = location_soup.find("meta",{'itemprop':"longitude"})["content"]
    store = []
    store.append("https://checkintocash.com")
    store.append(name)
    store.append(street_address)
    store.append(city)
    store.append(state)
    store.append(store_zip)
    store.append("US")
    store.append(url.split("-")[-1].replace(".html",""))
    store.append(phone if phone != "" else "<MISSING>")
    store.append("<MISSING>")
    store.append(lat)
    store.append(lng)
    store.append(hours)
    store.append(url)
    return store

def request_wrapper(url,method,headers,data=None):
    request_counter = 0
    if method == "get":
        while True:
            try:
                r = session.get(url,headers=headers)
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
                    r = session.post(url,headers=headers,data=data)
                else:
                    r = session.post(url,headers=headers)
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

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://checkintocash.com"
    r = session.get("https://local.checkintocash.com/index.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for states in soup.find_all("a",{'class':"c-directory-list-content-item-link"}):
        if states["href"].count("/") == 2:
            location_request = request_wrapper("https://local.checkintocash.com/" + states["href"].replace("../",""),"get",headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            store_data = parser(location_soup,"https://local.checkintocash.com/" + states["href"])
            yield store_data
        else:
            state_request = request_wrapper("https://local.checkintocash.com/" + states["href"],"get",headers=headers)
            state_soup = BeautifulSoup(state_request.text,"lxml")
            for city in state_soup.find_all("a",{'class':"c-directory-list-content-item-link"}):
                if city["href"].count("/") == 2:
                    location_request = request_wrapper("https://local.checkintocash.com/" + city["href"].replace("../",""),"get",headers=headers)
                    location_soup = BeautifulSoup(location_request.text,"lxml")
                    store_data = parser(location_soup,"https://local.checkintocash.com/" + city["href"].replace("../",""))
                    yield store_data
                else:
                    city_request = request_wrapper("https://local.checkintocash.com/" + city["href"].replace("../",""),"get",headers=headers)
                    city_soup = BeautifulSoup(city_request.text,"lxml")
                    for location in city_soup.find_all("a",{'class':"c-directory-list-content-item-link"}):
                        location_request = request_wrapper("https://local.checkintocash.com/" + location["href"].replace("../",""),"get",headers=headers)
                        location_soup = BeautifulSoup(location_request.text,"lxml")
                        store_data = parser(location_soup,"https://local.checkintocash.com/" + location["href"].replace("../",""))
                        yield store_data


def scrape():
    data = fetch_data()
    write_output(data)

scrape()