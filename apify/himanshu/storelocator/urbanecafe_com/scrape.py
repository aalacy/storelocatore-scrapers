import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import time

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
    base_url = "https://urbanecafe.com/"
    # for i in range(1,40):
    location_url = "https://urbanecafe.com/locations/"
    r = request_wrapper(location_url,"get",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    data = (soup.find_all("script",{"type":"text/javascript"})[-2]).text.split('-ajax.php","locations":')[1].split("};")[0]
    json_data = json.loads(data)
    for i in json_data:
        street_address = (i['street_address'])
        city = i['city']
        state = i['state']
        zipp = i['zip']
        country_code = "United States"
        latitude = i['map']['lat']
        longitude = i['map']['lng']
        phone = i['phone_number']
        location_name = i['title']
        store_number = i['ID']
        page_url = i['permalink']
        hours_of_operation = str(i['hours']).replace("[{'day_of_week': ",'').replace(", 'opening_hours': "," - ").replace("'","").replace(', closing_hours: '," - ").replace('}, {day_of_week: ',", ").replace("}]","")
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append(country_code if country_code else "<MISSING>")
        store.append(store_number if store_number else"<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("Urbanecafe")
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
