import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time 

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
def request_wrapper(url,method,headers,data=None):
   request_counter = 0
   if method == "get":
       while True:
           try:
               r = session.get(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   elif method == "post":
       while True:
           try:
               if data:
                   r = session.post(url,headers=headers,data=data)
               else:
                   r = session.post(url,headers=headers)
               return r
               break
           except:
               time.sleep(2)
               request_counter = request_counter + 1
               if request_counter > 10:
                   return None
                   break
   else:
       return None
def fetch_data():
    address = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url = "https://kelleysmarket.com"
    location_url = "https://kelleysmarket.com/locations/search"
    r = request_wrapper(location_url,"get",headers=headers).json()
    k = (r['locations'])
    for i in k:
        street_address = (i['address'])
        city = (i['city'])
        state = (i['state'])
        zipp = (i['zip'])
        location_name = i['title']
        url ="https://kelleysmarket.com/locations"
        country_code = "US"
        latitude = i['coordinates'][0]
        longitude = i['coordinates'][1]
        location_type =  ""
        phone = ""
        mp = location_name.replace(" ","-").replace(".","")
        new_url = "https://kelleysmarket.com/locations/location/"+str(mp)
        r = request_wrapper(new_url,"get",headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        data = soup.find("div",{"class":"loc-head"}).find("p")
        data2= re.sub(r'\s+', ' ', str(data))
        data1 = BeautifulSoup(data2,"lxml")
        hours_of_operation = (data1.text.strip().lstrip().rstrip())
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append("<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hours_of_operation if hours_of_operation else"<MISSING>")
        store.append(url if url else "<MISSING>")
        if store[2] in address :
            continue
        address.append(store[2])
        yield store 

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
