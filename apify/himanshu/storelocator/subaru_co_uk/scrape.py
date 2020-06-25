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
    MAX_RESULTS = 50
    MAX_DISTANCE = 20
    search = sgzip.ClosestNSearch()
    search.initialize(country_codes=['UK'])
    coord = search.next_coord()
    current_results_len = 0
    adressessess = []
    response=''
    base_url = "https://www.subaru.co.uk/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    url="https://www.subaru.co.uk/wp-admin/admin-ajax.php?action=store_search&lat=55.8262245&lng=-3.2496168&max_results=100&search_radius=500"
    # location_url = "https://www.subaru.co.uk/wp-admin/admin-ajax.php?action=store_search&lat="+str(coord[0])+"&lng="+str(coord[1])+"&max_results=500&search_radius=500&autoload=1"
    r = request_wrapper(url,"get",headers=headers)
    try:
        soup = r.json()
        current_results_len = len(r.json())
    except:
        pass
    for mp1 in soup:
        location_name  = mp1['store'].replace("#038;",' ')
        street_address = mp1['address'].replace("#038;",' ')
        city = mp1['city']
        state = mp1['state']
        zipp = mp1['zip']
        if street_address in adressessess :
            continue
        adressessess.append(street_address)
        country_code = mp1['country']
        phone =  mp1['phone']
        latitude = mp1['lat']
        longitude = mp1['lng']
        hours_of_operation=''
        state=''
        phone=''
        page_url=''
        hours_of_operation=''
        if mp1["url"]:
            page_url =  mp1["url"]
            new_page_url =page_url+"/contact"
            #print(page_url+"/contact")

            r1 = request_wrapper(page_url+"/contact","get",headers=headers)
            try:
                soup1 = BeautifulSoup(r1.text, "lxml")
            except:
                pass
            try:
                new_page_url = mp1["url"]+soup1.find_all("div",{"class":"contact-location-box"})[-1].find("a")['href']
                page_url = mp1["url"]+soup1.find_all("div",{"class":"contact-location-box"})[-1].find("a")['href']
                r2 = request_wrapper(page_url,"get",headers=headers)
                soup3 = BeautifulSoup(r2.text, "lxml")
                # print("yes....................")
                # print( list(soup3.find_all("div",{"class":"box flexi-height_child"})[1].stripped_strings))
                try:state = list(soup3.find_all("div",{"class":"box flexi-height_child"})[1].stripped_strings)[-3].strip().split(",")[-2]
                except:pass
                try:phone = soup3.find("p",class_="telephone-box").text.strip().replace("Telephone: ",'')
                except:pass
                hours_of_operation = " ".join(list(soup3.find("div",{"class":"opening-times-container"}).find("div",{"class":"row"}).stripped_strings))
            except:
                try:state = list(soup1.find_all("div",{"class":"box flexi-height_child"})[1].stripped_strings)[-3].strip().split(",")[-2]
                except:pass
                try:phone = soup1.find("p",class_="telephone-box").text.strip().replace("Telephone: ",'')
                except:pass
                try:hours_of_operation = " ".join(list(soup1.find("div",{"class":"opening-times-container"}).find("div",{"class":"row"}).stripped_strings))
                except:pass
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
        store.append(new_page_url if new_page_url else "<MISSING>")
        #print("~~~~~~~~~~~~~~~~ ",store)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()


