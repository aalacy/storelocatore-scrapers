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

def parser(location_soup,current_country,page_url):
    street_address = " ".join(list(location_soup.find("span",{'class':"c-address-street-1"}).stripped_strings))
    if location_soup.find("span",{'class':"c-address-street-2"}) != None:
        street_address = street_address + " " +  " ".join(list(location_soup.find("span",{'class':"c-address-street-2"}).stripped_strings))
    name = " ".join(list(location_soup.find("span",{'class':"LocationName"}).stripped_strings))
    city = location_soup.find("span",{'class':"c-address-city"}).text
    state = location_soup.find("abbr",{'class':"c-address-state"}).text
    store_zip = location_soup.find("span",{'class':"c-address-postal-code"}).text
    phone = location_soup.find("div",{'itemprop':"telephone"}).text
    hours = " ".join(list(location_soup.find("table",{'class':"c-hours-details"}).stripped_strings))
    lat = location_soup.find("meta",{'itemprop':"latitude"})["content"]
    lng = location_soup.find("meta",{'itemprop':"longitude"})["content"]
    store = []
    store.append("https://rochester-big-and-tall.destinationxl.com")
    store.append(name)
    store.append(street_address)
    store.append(city)
    store.append(state)
    store.append(store_zip)
    store.append(current_country)
    store.append("<MISSING>")
    store.append(phone if phone != "" else "<MISSING>")
    store.append("dxl")
    store.append(lat)
    store.append(lng)
    store.append(hours)
    store.append(page_url)
    return store

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://rochester-big-and-tall.destinationxl.com"
    r = session.get("https://stores.dxl.com/index.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for country in soup.find_all("a",{'class':"Directory-listLink"}):
        if country.find("span").text == "Canada":
            current_country = "CA"
        elif country.find("span").text == "United States":
            current_country = "US"
        else:
            continue
        country_request = session.get("https://stores.dxl.com/" + country["href"])
        country_soup = BeautifulSoup(country_request.text,"lxml")
        for states in country_soup.find_all("a",{'class':"Directory-listLink"}):
            if states["href"].count("/") == 3:
                location_request = session.get("https://stores.dxl.com/" + states["href"].replace("../",""))
                location_soup = BeautifulSoup(location_request.text,"lxml")
                store_data = parser(location_soup,current_country,"https://stores.dxl.com/" + states["href"].replace("../",""))
                yield store_data
            else:
                state_request = session.get("https://stores.dxl.com/" + states["href"])
                state_soup = BeautifulSoup(state_request.text,"lxml")
                for city in state_soup.find_all("a",{'class':"Directory-listLink"}):
                    if city["href"].count("/") == 4:
                        location_request = session.get("https://stores.dxl.com/" + city["href"].replace("../",""))
                        location_soup = BeautifulSoup(location_request.text,"lxml")
                        store_data = parser(location_soup,current_country,"https://stores.dxl.com/" + city["href"].replace("../",""))
                        yield store_data
                    else:
                        city_request = session.get("https://stores.dxl.com/" + city["href"].replace("../",""))
                        city_soup = BeautifulSoup(city_request.text,"lxml")
                        for location in city_soup.find_all("a",{'class':"Teaser-titleLink"}):
                            location_request = session.get("https://stores.dxl.com/" + location["href"].replace("../",""))
                            location_soup = BeautifulSoup(location_request.text,"lxml")
                            store_data = parser(location_soup,current_country,"https://stores.dxl.com/" + location["href"].replace("../",""))
                            yield store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
