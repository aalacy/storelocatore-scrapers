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
    base_url = "https://www.nissan.co.uk"
    # for i in range(1,40):
    location_url = "https://www.nissan.co.uk/dealer-locator.html"
    r = request_wrapper(location_url,"get",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    data = (soup.find("script",{"type":"text/javascript"}).text.split('{"totalResults":195,"dealers":')[1].split("};")[0])
    json_data = json.loads(data)
    for i in json_data:
        page5 = ((i['id']).replace("gb_nissan_05","").replace("51894","1894").replace("1780","1932").replace("1700","1931").replace("1004","51004"))
        link = "https://www.nissan.co.uk/dealer-homepage."+str(page5)+".html"
        r = request_wrapper(link,"get",headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        data1 = (soup.find("script",{"type":"application/ld+json"}).text)
        json_data = json.loads(data1)
        location_name = json_data['name']
        street_address = json_data['address']['streetAddress']
        city = json_data['address']['addressLocality']
        state = json_data['address']['addressCountry']
        zipp = json_data['address']['postalCode']
        phone = json_data['telePhone']
        latitude = json_data['geo']['latitude']
        longitude = json_data['geo']['longitude']
        store_number = json_data['@id'].replace('gb_nissan_','')
        hours_of_operation = str(json_data['openingHours']).replace("[","").replace("]","").replace("'","").replace(":","").replace("Sa","Saturday :").replace("Mo-Fr","Monday-Friday :").replace("Su","Sunday :").replace("Mo","Monday :").replace("Tues","Tuesday :").replace("We","Wednesday :").replace("Th","Thursday :").replace("Fr","Friday :")
        page_url = link
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(location_name if location_name else "<MISSING>") 
        store.append(street_address if street_address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("UK")
        store.append(store_number if store_number else"<MISSING>") 
        store.append(phone if phone else "<MISSING>")
        store.append("<MISSING>")
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
