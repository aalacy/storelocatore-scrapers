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
def request_wrapper(url,method,headers,data=None):
   request_counter = 0
   if method == "get":
       while True:
           try:
               r = requests.get(url,headers=headers)
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
                   r = requests.post(url,headers=headers,data=data)
               else:
                   r = requests.post(url,headers=headers)
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
    base_url = "https://www.districttaco.com/"
    r = session.get("https://www.districttaco.com/pages/locations")
    soup = BeautifulSoup(r.text, "lxml")
    json_data = json.loads(re.sub(r'\s+'," ",soup.find(lambda tag: (tag.name == "script" and '"streetAddress"' in tag.text)).text).replace('" District Taco Siver Spring", "image":"http://a.mktgcdn.com/p/WAR_UGUfFs-wu4eExIrW0wFx1QLZI-cBZh7PvX08mF4/619x411.jpg",','" District Taco Siver Spring", "image":"http://a.mktgcdn.com/p/WAR_UGUfFs-wu4eExIrW0wFx1QLZI-cBZh7PvX08mF4/619x411.jpg","openingHours":'))
    data = (json_data['location'])
    for i in data :
        location_name = (i['name'].strip())
        phone = (i['telephone'])
        street_address = (i['address']['streetAddress'])
        city =(i['address']['addressLocality'])
        state = (i['address']['addressRegion'])
        zipp = (i['address']['postalCode'])
        country_code = "US"
        location_type = i["@type"]
        hours_of_operation = str(i['openingHours']).replace("[","").replace("]","").replace("'","").replace("Mo","Monday").replace("Tu","Tuesday").replace("We","Wednesday").replace("Th","Thursday").replace("Fr","Friday").replace("Sa","Saturday").replace("Su","Sunday")
        data1 = location_name.replace(" ","-").lower().replace("crossroads-center","crossroads").replace('tenlwytown',"tenleytown").replace("tysons","tysons-corner").replace("siver","silver").replace("king-of-prussia","king-prussia")
        page_url = "https://order.districttaco.com/menu/"+str(data1)
        r = request_wrapper(page_url,"get",headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        latitude = (soup.find("meta",{"property":"og:latitude"})['content'])
        longitude = (soup.find("meta",{"property":"og:longitude"})['content'])
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
        store.append(hours_of_operation if hours_of_operation else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        if store[2] in address :
            continue
        address.append(store[2])
        yield store 

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
