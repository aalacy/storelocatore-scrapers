import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import requests
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

def fetch_data():
    addresses = []
    headers = {
    'content-type': "application/x-www-form-urlencoded",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    }
    base_url = "https://healthcare.ascension.org"
    page = 1
    while True:
        r = session.get("https://healthcare.ascension.org/Locations?page="+str(page)+"&_ga=2.105111747.1523815939.1586604954-156676794.1586604954",headers=headers)
        soup = BeautifulSoup(r.text, "lxml")
        if soup.find("div",{"class":"location-block"}) == None:
            break
        for data in soup.find_all("div",{"class":"location-block"}):
            
            location_name = data.find("h3",{"class":"heading-sub"}).text.strip()
            addr = list(data.find("address",{"role":"presentation"}).stripped_strings)
            if "Suite" in addr[0]:
                street_address = addr[0].split("Suite")[0]
            else:
                street_address = addr[0].replace("2nd Floor","").strip()
            city = addr[-1].replace("Birmingham,,  AL  35242","Birmingham, AL 35242").split(",")[0]
            state = addr[-1].replace("Birmingham,,  AL  35242","Birmingham, AL 35242").split(",")[1].split(" ")[1]
            zipp = addr[-1].replace("Birmingham,,  AL  35242","Birmingham, AL 35242").split(",")[1].split(" ")[2]
            phone = data.find_all("div",{"class":"location-aux"})[-1].find("a").text.strip()
            location_type = re.sub(r'\s+'," ",data.find("ul",{"class":"location-type"}).text.strip())
            page_url = base_url+data.find("h3",{"class":"heading-sub"}).find("a")['href']
            latitude = data['data-lat']
            longitude = data['data-lng']

            
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp if zipp else "<MISSING>")
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append("<MISSING>")
            store.append(page_url)
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addresses:
                continue
            addresses.append(store[2]) 
            # print("data == "+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
        page+=1
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
