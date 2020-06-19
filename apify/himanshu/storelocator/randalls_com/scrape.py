import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import requests


session = SgRequests()

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
}

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def convert_time(time):
    temp_time = str(time)[:-2] + ":" + str(time)[-2:]
    is_am = "AM"
    hour = int(str(time)[:-2])
    if int(hour) < 12:
        is_am = "AM"
        hour = int(str(time)[:-2])
    else:
        is_am = "PM"
        hour = int(str(time)[:-2]) - 12
    return str(hour) + ":" + str(time)[-2:] + " " + is_am

def parser(location_soup,page_url):
    street_address = " ".join(list(location_soup.find("span",{'class':"c-address-street-1"}).stripped_strings))
    if location_soup.find("span",{'class':"c-address-street-2"}) != None:
        street_address = street_address + " " +  " ".join(list(location_soup.find("span",{'class':"c-address-street-2"}).stripped_strings))
    name = location_soup.find("span",{'class':"LocationName-geo"}).text.strip()
    city = location_soup.find("span",{'class':"c-address-city"}).text
    state = location_soup.find("abbr",{'class':"c-address-state"}).text
    store_zip = location_soup.find("span",{'class':"c-address-postal-code"}).text
    if location_soup.find("div",{'itemprop':"telephone"}) == None:
        phone = "<MISSING>"
    else:
        phone = location_soup.find("div",{'itemprop':"telephone"}).text
        # print(phone)
    ho1= location_soup.find("table",{"class":"c-hours-details"}).text
    # c-hours-details 
    ho = (ho1.replace('PM',"PM ").replace("Day of the WeekHours","Store Hours ").replace("y","y ").strip())
    hours = ""
    hours =  location_soup.find_all("div",{"class":"Core-hoursSection"})[-1].text.split('Day of the WeekHours')[1].replace("Visit Pharmacy Page","").replace('PM',"PM ").replace("y","y ").strip()
    hours_of_operation = (str(ho)+", Pharmacy Hours : "+str(hours))
    if "2727 Exposition Blvd" in street_address:
        hours_of_operation = str(ho)
    lat = location_soup.find("meta",{'itemprop':"latitude"})["content"]
    lng = location_soup.find("meta",{'itemprop':"longitude"})["content"]
    store = []
    store.append("https://randalls.com")
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
    store.append(hours_of_operation)
    store.append(page_url)
    return store

def fetch_data():
    base_url = "https://randalls.com"
    r = requests.get("https://local.randalls.com/index.html",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for states in soup.find_all("a",{'class':"Directory-listLink"}):
        # print("https://local.randalls.com/"+states["href"])
        
        if states["href"].count("/") == 2:
            
            location_request = requests.get("https://local.randalls.com/" + states["href"].replace("../",""),headers=headers)
            location_soup = BeautifulSoup(location_request.text,"lxml")
            
            
            store_data = parser(location_soup,"https://local.randalls.com/" + states["href"].replace("../",""))
            yield store_data
        else:
            
            state_request = requests.get("https://local.randalls.com/" + states["href"],headers=headers)
            
            state_soup = BeautifulSoup(state_request.text,"lxml")
            # print(state_soup)
            for city in state_soup.find_all("a",{'class':"Directory-listLink"}):
                if city["href"].count("/") == 2:
                    
                    location_request = requests.get("https://local.randalls.com/" + city["href"].replace("../",""),headers=headers)
                    location_soup = BeautifulSoup(location_request.text,"lxml")
                    store_data = parser(location_soup,"https://local.randalls.com/" + city["href"].replace("../",""))
                    yield store_data
                else:
                    
                    city_request = requests.get("https://local.randalls.com/" + city["href"].replace("../",""),headers=headers)
                    # print(city_request)
                    city_soup = BeautifulSoup(city_request.text,"lxml")
                    
                    for location in city_soup.find_all("a",{'class':"Teaser-titleLink"}):
                        
                        location_request = requests.get("https://local.randalls.com/" + location["href"].replace("../",""),headers=headers)
                        location_soup = BeautifulSoup(location_request.text,"lxml")
                        store_data = parser(location_soup,"https://local.randalls.com/" + location["href"].replace("../",""))
                        yield store_data
def scrape():
    data = fetch_data()
    write_output(data)


scrape()


