import csv
from bs4 import BeautifulSoup
import re
import json
import time
import html5lib
from sgrequests import SgRequests
from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('nissan_co_uk')
session = SgRequests() 
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline="") as output_file:
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
    data = ["https://www.nissan.co.uk/dealer-list.html","https://www.nissan.co.uk/dealer-list/k-z.html"]
    for g in data :
        r = request_wrapper(g,"get",headers=headers)
        soup = BeautifulSoup(r.text,"html5lib")
        data = (soup.find_all("div",{"class":"c_153"}))
        for i in data:
            link = (i.find_all("td")[2].find("a")['href'])
            r = request_wrapper(link,"get",headers=headers)
            soup = BeautifulSoup(r.text,"html5lib")
            try:
                data1 = (soup.find("script",{"type":"application/ld+json"}).text)
            except:
                continue
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
            store.append(street_address.strip().replace("         ","") if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("UK")
            store.append(store_number if store_number else"<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("Nissan - Dealer | Nissan UK")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append("<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            if store[7] in address :
                continue
            address.append(store[7])
            yield store 
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
