# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json,urllib
import time
import lxml


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.accesshealthdental.com/locations/"

    r = session.get(base_url )
    soup = BeautifulSoup(r.text,"lxml")
    for div in soup.find_all("div",{"class":"su-tabs-pane su-u-clearfix su-u-trim"})[1:]:
        location_name = div['data-title']
        data = list(div.stripped_strings)

        if len(data) == 35:
            street_address = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            zipp = "<MISSING>"
            phone = data[2].replace(".","")
        elif len(data) == 10:
            street_address = data[1]
            city = data[2].split(",")[0]
            state = data[2].split(",")[1].split()[0]
            zipp = data[2].split(",")[1].split()[1]
            phone = data[4]
        else:
            
            street_address = data[-2]
            if "," in data[-1]:
                city = data[-1].split(",")[0]
                state = data[-1].split(",")[1].split()[0]
                zipp = data[-1].split(",")[1].split()[1] 
            else:
                city = " ".join(data[-1].split()[:-2])
                state = data[-1].split()[-2]
                zipp = data[-1].split()[-1]
            phone = data[2].replace(".","")
        if "!3d" in div.iframe.get('src'):
            latitude = div.iframe.get('src').split('3d')[1].split('!2')[0]
            longitude = div.iframe.get('src').split("!2d")[1].split('!3d')[0]
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
    
        store = []
        store.append("https://www.accesshealthdental.com")
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(base_url)
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
    



def scrape():
    data = fetch_data()
    write_output(data)

scrape()
