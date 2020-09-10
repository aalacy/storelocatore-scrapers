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
    with open('data.csv', mode='w') as output_file:
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
    location_url = "https://papa-murphys-order-online-locations.securebrygid.com/zgrid/themes/13097/portal/index.jsp"   
    r = session.get(location_url, headers=headers)   
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("div",{"class":"restaurant"})
    for i in data:
        t = list(i.stripped_strings)
        if "ONLINE ORDERING COMING SOON" in t:
            continue
        
        if "Skip The Dishes - Delivery" in t[-1]:
            del t[-1] 
        if "Order Online" in t[-1]:
            del t[-1]
        location_name = t[0]
        street_address = t[1]
        city = t[2].split(',')[0]
        state = t[2].split(',')[1].split(' ')[1]
        zipp = ' '.join(t[2].split(',')[1].split(' ')[2:])
        phone = t[3]
        hours_of_operation=''
        for index,dt in enumerate(t):
            if "Get Directions" in dt:
                hours_of_operation= " ".join(t[index+1:])
        # hours_of_operation = ' '.join(t[5:8]).replace("*delivery available from 4pm to close.",'').replace("Delivery: 11am - Close",'')
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("CA")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours_of_operation)
        store.append(location_url)
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        # print(store)
        yield store
        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
