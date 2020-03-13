import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import datetime
from datetime import datetime
import requests
import itertools as it
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    addresses = []
   
    base_url = "https://www.waitrose.com/"
  
    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36,'
    }
    r = requests.get("https://www.waitrose.com/content/waitrose/en/bf_home/bf/689.html",headers=headers )
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find_all("option")
    
    for value in it.chain(range(100,975), range(1250,1260)):
        # print(value)
        if value == "":
            continue
        page_url = "https://www.waitrose.com/content/waitrose/en/bf_home/bf/"+str(value)+".html"
        # print(page_url)
        
        r1 = requests.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        if soup1.find("div",{"class":"col branch-details"}) == None:
            # print(page_url)
            continue

        try:
            location_name = soup1.find("h1",{"class":"pageTitle"}).text.replace("Welcome to little","").replace("Welcome to Little",'').replace("Welcome to",'').strip()
        except:
            location_name = soup1.find("div",{"class":"title"}).text.replace("Welcome to little","").strip()

        addr = list(soup1.find("div",{"class":"col branch-details"}).stripped_strings)
        try: 
            if len(addr) == 6:
                street_address = " ".join(addr[:2])
                city = addr[2]
                state = addr[-3]
                zipp = addr[-2]
                phone = addr[-1]
            else:
                street_address = addr[0]
                city = addr[1]
                state = addr[-3]
                zipp = addr[-2]
                phone = addr[-1]

        except:
            pass 
        else:
            if street_address == "STREET_ADDR" and city == "BRANCH_PHONE_NUM" and zipp == "STREET_ADDR" and phone == "BRANCH_PHONE_NUM":
                street_address = "<MISSING>"
                city = "<MISSING>"
                zipp = "<MISSING>"
                phone = "<MISSING>"


        try:  
            latitude = soup1.find("a",{"class":"secondary load-branch-map"})['data-lat']
            longitude = soup1.find("a",{"class":"secondary load-branch-map"})['data-long']
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        else:
            if latitude == "0.00000" and latitude == "0.00000":
                latitude = "<MISSING>"
                longitude = "<MISSING>"




        #print(latitude, longitude)
        store_number = value
        hours_of_operation = " ".join(list(soup1.find("table").stripped_strings))
        store = []
        store.append(base_url)
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")   
        store.append("UK")
        store.append(store_number if store_number else "<MISSING>") 
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        # if store[2] in addresses:
        #         continue
        # addresses.append(store[2])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
