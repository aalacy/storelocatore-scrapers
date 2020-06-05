import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time
from sgrequests import SgRequests
session = SgRequests() 
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url = "https://www.kia.com/uk/"
    
   
    json_data = session.get("https://www.kia.com/api/kia_uk/findByDealer.list?displayYn=Y&delYn=N&pagePerLines=99999999&locale=undefined-undefined&usedSellYn=N&servicingYn=Y",headers=headers).json()['data']['list']
    
   
    for data in json_data:
        location_name  = data['dealerName']
        zipp = data['postcode']
        street_address = ''
        state = ''
        if data['address1']:
            street_address+= data['address1']
        if data['address2']:
            street_address+= "|"+data['address2']
        if data['address3']:
            street_address+= "|"+data['address3']
        if data['address4']:
            street_address+= "|"+data['address4']
        if data['address5']:
            street_address+= "|"+data['address5']
        if data['address6']:
            street_address+= "|"+data['address6']

        addr = street_address.strip().split("|")
        if len(street_address.strip().split("|")) == 2:
            street_address = addr[0]
            city = addr[-1].replace(zipp,"").strip()

        elif len(street_address.strip().split("|")) == 3:
            street_address = addr[0]
            city = addr[1].replace(zipp,"")
            state = addr[-1].replace(zipp,"").strip()
        elif len(street_address.strip().split("|")) == 4:
            if zipp in addr[-1]:
                del addr[-1]
            if len(addr) == 3:
                street_address = addr[0]
                city = addr[1].replace(zipp,"")
                state = addr[-1].replace(zipp,"")
            else:
                street_address = " ".join(addr[:-2])
                city = addr[-2].replace("-","").replace(zipp,"").strip()
                state = addr[-1].replace(zipp,"")
        else:
            street_address = " ".join(addr[:-2])
            city = addr[-2].replace("-","").replace(zipp,"").strip()
            state = addr[-1].replace(zipp,"")

       
        
        country_code = "UK"
        phone =  data['salesPhone']
        lat = data['latitude']
        lng = data['longitude']
        
        page_url = "https://www."+str(data["url"])
        hours_of_operation = str(data['salesHours']).replace("[{'name': ","").replace(", 'hours'"," ").replace("'","").replace("}]","").replace('{',"").replace('}',"").replace(" name:","")
        if hours_of_operation =="None":
            hours_of_operation = "<MISSING>"
        store_number = data['dealerSeq']



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
        store.append(lat)
        store.append(lng)
        store.append(hours_of_operation)
        store.append(page_url)     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
       
        yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
