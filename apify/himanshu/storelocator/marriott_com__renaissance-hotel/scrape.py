import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
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
    base_url = "https://renaissance-hotels.marriott.com"
    location_url = "https://renaissance-hotels.marriott.com/locations-list-view"
    r = request_wrapper(location_url,"get",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    data = soup.find_all("script",{"type":"text/javascript"})[7]
    k = (data.text.split('renaissance":{"locations":')[1].split('},"js":{"tokens"')[0])
    json_data = json.loads(k)
    for i in json_data:
        mp = (i['url'])
        r1 = request_wrapper(mp,"get",headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        data = soup1.find(lambda tag : (tag.name == "script") and "addressLocality" in tag.text).text.replace("\r\n",'')
        fdata  = (json.loads(re.sub(r'\s+'," ",data)))
        for h in fdata['contactPoint']:
            if 'telephone' in h:
                phone = (h['telephone'])
                zipp = fdata['address']['postalCode'].replace("OK ","").replace("NY ","")
                store = []
                store.append(base_url if base_url else "<MISSING>")
                store.append(fdata['name'] if fdata['name'] else "<MISSING>") 
                store.append(fdata['address']['streetAddress'] if fdata['address']['streetAddress'] else "<MISSING>")
                store.append(fdata['address']['addressLocality'] if fdata['address']['addressLocality'] else "<MISSING>")
                store.append(fdata['address']['addressRegion'] if fdata['address']['addressRegion'] else "<MISSING>")
                store.append( zipp if zipp else "<MISSING>")
                store.append(fdata['address']['addressCountry'] if fdata['address']['addressCountry'] else "<MISSING>")
                store.append("<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append(fdata['branchOf']['name'] if fdata['branchOf']['name'] else "<MISSING>")
                store.append(fdata['geo']['latitude'] if fdata['geo']['latitude'] else "<MISSING>")
                store.append(fdata['geo']['longitude'] if fdata['geo']['longitude'] else "<MISSING>")
                store.append("<MISSING>")
                store.append(fdata['url'] if fdata['url'] else "<MISSING>")
                store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                if store[2] in address :
                    continue
                address.append(store[2])
                if fdata['address']['addressCountry'] == 'United States' or fdata['address']['addressCountry'] == 'USA' or fdata['address']['addressCountry'] =='Canada' or fdata['address']['addressCountry'] =='' or fdata['address']['addressCountry'] =='United States Virgin Islands':
                    yield store 

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
