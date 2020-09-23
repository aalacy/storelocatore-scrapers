# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import http.client
session = SgRequests()
http.client._MAXHEADERS = 1000

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    
    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        
    }

    base_url = "http://papamurphys.ca/"
    location_url = "https://order.papamurphys.com/locations"   
    r = session.get(location_url, headers=headers)   
    soup = BeautifulSoup(r.text, "lxml")
    for href in soup.find("ul",{"id":"ParticipatingStates"}).find_all("a"):
        r1 = session.get("https://order.papamurphys.com"+href['href'], headers=headers)   
        soup1 = BeautifulSoup(r1.text, "lxml")
        for h1 in soup1.find("ul",{"id":"ParticipatingRestaurants"}).find_all("a"):
            page_url = h1['href']
            r2 = session.get(page_url, headers=headers)   
            soup2 = BeautifulSoup(r2.text, "lxml")
            street_address = soup2.find("span",{"class":"street-address"}).text.strip()
            city = soup2.find("span",{"class":"locality"}).text.strip()
            location_name = soup2.find("div",{"class":"fn org"}).find("h1").text.strip()
            state = soup2.find("span",{"class":"region"}).text.strip()
            zipp = soup2.find("span",{"class":"postal-code"}).text.strip()
            lat = soup2.find("span",{"class":"geo"}).find("span",{"class":"latitude"}).find("span",{"class":"value-title"})['title']
            longs = soup2.find("span",{"class":"geo"}).find("span",{"class":"longitude"}).find("span",{"class":"value-title"})['title']
            phone = soup2.find("span",{"class":re.compile("tel")}).text.strip()
            hours_of_operation = ''
            for q in soup2.find_all("dl",{"class":"available-hours"}):
                hours_of_operation = hours_of_operation + ' '+ " ".join(list(q.stripped_strings))
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
            store.append(lat)
            store.append(longs)
            store.append(hours_of_operation)
            store.append(page_url)
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            # print(store)
            yield store
            


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
