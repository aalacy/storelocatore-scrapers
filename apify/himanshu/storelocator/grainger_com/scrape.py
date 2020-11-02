import csv
from bs4 import BeautifulSoup
import re
import json
import time
import html5lib
from sgrequests import SgRequests
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
    base_url = "https://www.grainger.com/"
    location_url = ("https://www.grainger.com/rservices/branch/find/100000/1?searchBox=21216&latitude=39.30969839999999&longitude=-76.6701475&miles=100000&itemNumber=10000&productQty=&_=1601534968603")
    r = request_wrapper(location_url,"get",headers=headers)
    json_data1 = json.loads(r.text)
    json_data = (json_data1['payload']['branches'])
    for i in json_data:
        store = []
        store.append(base_url if base_url else "<MISSING>")
        store.append(i['branchURL'].split("/branch/")[1].split("?")[0].replace("-"," ").replace("Branch ","Branch #") if i['branchURL'] else "<MISSING>") 
        store.append(i['branchAddress']['address1'] if i['branchAddress']['address1'] else "<MISSING>")
        store.append(i['branchAddress']['city'] if i['branchAddress']['city'] else "<MISSING>")
        store.append(i['branchAddress']['state'] if i['branchAddress']['state'] else "<MISSING>")
        store.append(i['branchAddress']['zipCode'][0:5] if i['branchAddress']['zipCode'][0:5] else "<MISSING>")
        store.append(i['branchAddress']['country'] if i['branchAddress']['country'] else "<MISSING>")
        store.append(i['branchCode'] if i['branchCode'] else"<MISSING>") 
        store.append(i['telephone'] if i['telephone'] else "<MISSING>")
        store.append(i['branchType'] if i['branchType'] else "<MISSING>")
        store.append(i['latitude'] if i['latitude'] else "<MISSING>")
        store.append(i['longitude'] if i['longitude'] else "<MISSING>")
        store.append(i['weekdayHours'] if i['weekdayHours'] else "<MISSING>")
        store.append("https://www.grainger.com/"+i['branchURL'] if "https://www.grainger.com/"+i['branchURL'] else "<MISSING>")
        if store[2] in address :
            continue
        address.append(store[2])
        yield store 
def scrape():
    data = fetch_data()
    write_output(data)
scrape()