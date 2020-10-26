import csv
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
    base_url = "https://sheraton.marriott.com"
    location_url = "https://sheraton.marriott.com/"
    r = request_wrapper(location_url,"get",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    # print(soup)
    data = soup.find_all("script",{"type":"text/javascript"})[5]
    mp = (data.text.split("MARRIOTT_GEO_DATA = ")[1].replace(':"WI"}};',':"WI"}}'))
    json_data = json.loads(mp)
    canada = (json_data['tree']['north.america']['countries']['CA']['cities'])
    for i in canada:
        city = canada[i]['name']
        k = (canada[i]['properties'].keys())
        for j in k:
            key  = (j)
            mp1 = (canada[i]['properties'][j])
            location_name  = mp1['name']
            street_address = mp1['address']
            state = mp1['state']
            zipp = mp1['zipcode']
            country_code = mp1['country']
            phone =  mp1['phone']
            latitude = mp1['latitude']
            longitude = mp1['longitude']
            data = street_address.lower().replace(" ","-")
            page_url = "https://www.marriott.com/hotels/travel/"+str(key)
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
            store.append("Sheraton Hotels and Resorts")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append("<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store 
    United_state = (json_data['tree']['north.america']['countries']['US']['states'])
    for i1 in United_state:
        state = United_state[i1]['name']
        k1 = (United_state[i1]['properties'].keys())
        for j1 in k1:
            key  = (j1)
            mp2 = (United_state[i1]['properties'][j1])
            location_name  = mp2['name']
            street_address = mp2['address']
            city =" ".join(mp2['city'].split("_us_us")[0].split("_")[:-1])
            zipp = mp2['zipcode']
            country_code = mp2['country']
            phone =  mp2['phone']
            latitude = mp2['latitude']
            longitude = mp2['longitude']
            data = street_address.lower().replace(" ","-")
            page_url = "https://www.marriott.com/hotels/travel/"+str(key)
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
            store.append("Sheraton Hotels and Resorts")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append("<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[2] in address :
                continue
            address.append(store[2])
            yield store
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
