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
    # addresses = []
    # r_headers = {
    #     'Accept': '*/*',
    #     'Content-Type': 'application/json; charset=UTF-8',    
        
    # }
    headers = {
    'content-type': "application/x-www-form-urlencoded",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    }
    base_url = "https://www.tenethealth.com"
    r = session.get("https://viewer.blipstar.com/searchdbnew?uid=2470030&lat=51.5284541234394&lng=-0.154586637827429&type=nearest&value=6000&keyword=&max=10000&sp=NW1&ha=no&htf=1&son=&product=&product2=&product3=&cnt=&acc=&mb=false&state=&ooc=0&r=0.09512541287984777",headers=headers).json()
    addressesess=[]
    CountryCode = "US"
    for index,anchor in enumerate(r):
        if index >=1:
            soup = BeautifulSoup(anchor['a'],'lxml')
            state = soup.find("span",{"class":"storecity"}).text.lower()
            zipp = soup.find("span",{"class":"storepostalcode"}).text
            street_address = anchor['ad'].split(",")[0]
            city = anchor['ad'].split(",")[1].strip().lower()
            location_name = anchor['n']
            if anchor["w"]:
                page_url =  anchor["w"]
            else:
                page_url = "<MISSING>"
            phone = anchor['p']
            hours ='mon '+anchor['mon']+ ' tue ' + anchor['tue']+' wed '+ anchor['wed']+ ' thu ' + anchor['thu']+' fri '+anchor['fri']+' sat '+anchor['sat']+' sun '+anchor['sun']
            location_type = "<MISSING>"
            latitude = anchor['lat']
            longitude = anchor['lng']
            store = []
            store.append('http://ladbrokes.com')
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp if zipp else "<MISSING>")
            store.append("UK")
            store.append("<MISSING>")
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            if store[2] in addressesess:
                continue
            addressesess.append(store[2])
            # print("data == "+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
