import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip
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
    MAX_RESULTS = 60
    MAX_DISTANCE = 100
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['UK'])
    coord = search.next_coord()
    current_results_len = 0
    adressessess = []
   
    response=''
    base_url = "https://www.subaru.co.uk/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    
    while coord:
        # print("remaining zipcodes: " + str(len(search.zipcodes)))
        result_coords =[]
        location_url = "https://www.subaru.co.uk/wp-admin/admin-ajax.php?action=store_search&lat="+str(coord)+"&lng="+str(coord)+"&max_results=25&search_radius=50&autoload=1"
        r = request_wrapper(location_url,"get",headers=headers)
        try:
            soup = r.json()
            response = len(r.json())
        except:
            pass
        for mp1 in soup:
            location_name  = mp1['store'].replace("#038;",' ')
            street_address = mp1['address'].replace("#038;",' ')
            city = mp1['city']
            state = mp1['state']
            zipp = mp1['zip']
            country_code = mp1['country']
            phone =  mp1['phone']
            latitude = mp1['lat']
            longitude = mp1['lng']
            page_url = mp1["url"]
            hours_of_operation=''
            state=''
            phone=''
            hours_of_operation=''
            if page_url:
                # print(page_url+'/contact')
                try:
                    r1 = request_wrapper(page_url+'/contact',"get",headers=headers)
                except:
                    pass
                try:
                    soup1 = BeautifulSoup(r1.text, "lxml")
                    state = list(soup1.find_all("div",{"class":"box flexi-height_child"})[1].stripped_strings)[-3].strip().split(",")[-2]
                except:
                    state=''
                try:
                    phone = soup1.find("p",class_="telephone-box").text.strip().replace("Telephone: ",'')
                except:
                    phone=""
                try:
                    hours_of_operation = " ".join(list(soup1.find("div",{"class":"opening-times-container"}).find("div",{"class":"row"}).stripped_strings))
                except:
                    hours_of_operation=''
            # hours_of_operation = (mp1['hours']).replace('</time></td></tr><tr><td>',", ").replace("</td><td><time>"," ").replace('</td><td>Closed</td></tr><tr><td>'," Closed,").replace("</td><td>Closed</td></tr></table>"," Closed").replace("<table role=""presentation"" class=""wpsl-opening-hours"">"," ")
            store_number = mp1['id']
            store = []
            store.append(base_url)
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append(country_code if country_code else "<MISSING>")
            store.append(store_number if store_number else"<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else "<MISSING>")
            store.append(hours_of_operation.replace('\n','').strip() if hours_of_operation else "<MISSING>")
            store.append(page_url if page_url else "<MISSING>")
            # print("~~~~~~~~~~~~~~~~ ",store)
            if store[2] in adressessess :
                continue
            adressessess.append(store[2])
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            yield store
        if response < MAX_RESULTS:
            # print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        elif response == MAX_RESULTS:
            # print("max count update")
            search.max_count_update(result_coords)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coords = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)
scrape()


