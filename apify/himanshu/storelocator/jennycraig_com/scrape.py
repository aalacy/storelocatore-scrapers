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
    name = " ".join(list(location_soup.find("div",{'id':"rls_loc_name"}).stripped_strings))
    street_address = location_soup.find("meta",{'property':re.compile("street-address")})["content"].replace(","," ").replace("  ","")
    city = location_soup.find("meta",{'property':re.compile("locality")})["content"]
    state = location_soup.find("meta",{'property':re.compile("region")})["content"]
    store_zip = location_soup.find("meta",{'property':re.compile("postal-code")})["content"]
    if location_soup.find("meta",{'property':re.compile("phone_number")}) == None:
        phone = "<MISSING>"
    else:
        phone = location_soup.find("meta",{'property':re.compile("phone_number")})["content"]
    country = location_soup.find("meta",{'property':re.compile("country-name")})["content"]
    if country == "PR":
        country = "US"
    hours = " ".join(list(location_soup.find("div",{'id':"rls_loc_hours"}).stripped_strings)).split("if(typeof")[0]
    lat = location_soup.find("meta",{'property':re.compile("latitude")})["content"]
    lng = location_soup.find("meta",{'property':re.compile("longitude")})["content"]
    store = []
    store.append("https://jennycraig.com")
    store.append(name)
    store.append(street_address)
    store.append(city)
    store.append(state)
    store.append(store_zip)
    store.append(country)
    store.append("<MISSING>")
    store.append(phone if phone != "" else "<MISSING>")
    store.append("<MISSING>")
    store.append(lat)
    store.append(lng)
    store.append(hours)
    store.append(url)
    return store

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    addresses = []
    base_url = "https://jennycraig.com"
    r = session.get("https://locations.jennycraig.com",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    for states in soup.find_all("a",{'class':"regionlist gaq-link"}):
        # print(states["href"])
        state_request = session.get(states["href"],headers=headers)
        state_soup = BeautifulSoup(state_request.text,"lxml")
        for city in state_soup.find_all("a",{'class':"citylist gaq-link"}):
            # print(city["href"])
            city_request = session.get(city["href"],headers=headers)
            city_soup = BeautifulSoup(city_request.text,"lxml")
            for location in city_soup.find("div",{"class":'tlsmap_list'}).find_all("div",recursive=False):
                location_url = location.find("a")['href']
                location_request = session.get(location_url,headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                store_data = parser(location_soup,location_url)
                if store_data[6] not in ["US","CA"]:
                    continue
                if store_data[2] in addresses:
                    continue
                addresses.append(store_data[2])
                yield store_data

                
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
