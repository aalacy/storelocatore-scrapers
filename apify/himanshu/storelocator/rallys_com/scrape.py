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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def parser(location_soup,url):
    if location_soup.find("div",{'class':"c-AddressRow"}) != None:
        street_address = " ".join(list(location_soup.find("div",{'class':"c-AddressRow"}).stripped_strings))
        name = " ".join(list(location_soup.find("span",{'class':"LocationName"}).stripped_strings))
        city = location_soup.find("span",{'class':"c-address-city"}).text
        state = location_soup.find("abbr",{'class':"c-address-state"}).text
        store_zip = location_soup.find("span",{'class':"c-address-postal-code"}).text
        phone = location_soup.find("span",{'itemprop':"telephone"}).text
        hours = " ".join(list(location_soup.find("table",{'class':"c-location-hours-details"}).stripped_strings))
        lat = location_soup.find("meta",{'itemprop':"latitude"})["content"]
        lng = location_soup.find("meta",{'itemprop':"longitude"})["content"]
        page_url = url
        

    else:
        
        street_address = "<MISSING>"
        name = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        store_zip = "<MISSING>"
        phone = "<MISSING>"
        hours = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        page_url = url

    
    store = []
    store.append("https://rallys.com")
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
    store.append(page_url)

    return store

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://rallys.com"
    r = session.get("https://locations.rallys.com/index.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for states in soup.find_all("li",{'class':"c-directory-list-content-item"}):
        if states.find("a")["href"].count("/") == 2:
            location_request = session.get("https://locations.rallys.com/" + states.find("a")["href"])
            location_soup = BeautifulSoup(location_request.text,"lxml")
            url = "https://locations.rallys.com/" + states.find("a")["href"].replace("../","")
            store_data = parser(location_soup,url)
            return_main_object.append(store_data)
        else:
            state_request = session.get("https://locations.rallys.com/" + states.find("a")["href"])
            state_soup = BeautifulSoup(state_request.text,"lxml")
            for city in state_soup.find_all("li",{'class':"c-directory-list-content-item"}):
                if city.find("a")["href"].count("/") == 2:
                    location_request = session.get("https://locations.rallys.com/" + city.find("a")["href"])
                    location_soup = BeautifulSoup(location_request.text,"lxml")
                    url = "https://locations.rallys.com/" + city.find("a")["href"].replace("../","")
                    store_data = parser(location_soup,url)
                    return_main_object.append(store_data)
                else:
                    city_request = session.get("https://locations.rallys.com/" + city.find("a")["href"] )
                    city_soup = BeautifulSoup(city_request.text,"lxml")
                    for location in city_soup.find_all("li",{'class':"c-LocationGridList-item"}):

                        location_request = session.get("https://locations.rallys.com/" + location.find("a")["href"].replace("../",""))
                        if location_request.status_code != 200:
                            continue
                        url = "https://locations.rallys.com/" + location.find("a")["href"].replace("../","")
                        location_soup = BeautifulSoup(location_request.text,"lxml")
                        store_data = parser(location_soup,url)
                        return_main_object.append(store_data)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
