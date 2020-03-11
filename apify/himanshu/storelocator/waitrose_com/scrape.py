import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import datetime
from datetime import datetime
import requests
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    r = requests.get("https://www.waitrose.com/content/waitrose/en/bf_home/bf/474.html",headers=headers )
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find("select",{"id":"global-form-select-branch"}).find_all("option")
    for value in data:
        # print(value)
        if value['value'] == "":
            continue
        page_url = "https://www.waitrose.com/content/waitrose/en/bf_home/bf/"+str(value['value'])+".html"
        # print(page_url)s
        
        r1 = requests.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        if soup1.find("div",{"class":"col branch-details"}) == None:
            #print(page_url)
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
                state = "<INACCESSIBLE>"
                zipp = addr[-2]
                phone = addr[-1]
            else:
                street_address = addr[0]
                city = addr[1]
                state = "<INACCESSIBLE>"
                zipp = addr[-2]
                phone = addr[-1]
        except:
            pass 
        try:  
            latitude = soup1.find("a",{"class":"secondary load-branch-map"})['data-lat']
            longitude = soup1.find("a",{"class":"secondary load-branch-map"})['data-long']
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        store_number = value['value']
        hours_of_operation = " ".join(list(soup1.find("table").stripped_strings))
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("UK")
        store.append(store_number)
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude )
        store.append(longitude )
        store.append(hours_of_operation)
        store.append(page_url)
        if store[2] in addresses:
                continue
        addresses.append(store[2])
        yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
