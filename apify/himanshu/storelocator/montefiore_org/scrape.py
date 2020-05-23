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
    base_url = ""
    location_url = "https://www.montefiore.org/cancer-contact"
    base_url = 'https://www.montefiore.org/'
    r = request_wrapper(location_url,"get",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    data = (soup.find("div",{"class":"content"}))
    # phone = soup.find("div",{"class":"content"}).find("p").text.split(",")[1].split("Phone: ")[1]
    # zipp = soup.find("div",{"class":"content"}).find("p").text.split(",")[1].split("Phone: ")[0].split(" ")[2]
    # state = soup.find("div",{"class":"content"}).find("p").text.split(",")[1].split("Phone: ")[0].split(" ")[1]
    # street_address = soup.find("div",{"class":"content"}).find("p").text.split(",")[0].split("Care")[1].split("Bronx")[0]
    # city = soup.find("div",{"class":"content"}).find("p").text.split(",")[0].split("Care")[1].split("Street")[1]
    # location_name = soup.find("div",{"class":"content"}).find("p").text.split(",")[0].split("111")[0]
    # store = []
    # store.append(base_url if base_url else "<MISSING>")
    # store.append(location_name if location_name else "<MISSING>") 
    # store.append(street_address if street_address else "<MISSING>")
    # store.append(city if city else "<MISSING>")
    # store.append(state if state else "<MISSING>")
    # store.append(zipp if zipp else "<MISSING>")
    # store.append("US")
    # store.append("<MISSING>") 
    # store.append(phone if phone else "<MISSING>")
    # store.append("<MISSING>")
    # store.append("<MISSING>")
    # store.append("<MISSING>")
    # store.append("<MISSING>")
    # store.append(location_url if location_url else "<MISSING>")
    # yield store 
    data2 = data.find("table")
    mp = (data2.find_all("tr"))
    for i in mp:
        mp1 = (i.find_all("td"))
        link = i.find("a")
        
        for j in mp1  :
            full = list(j.stripped_strings)
            if len(full)!= 1 and full !=[]:
                
                try:
                    if link !=  None:
                        # print(link['href'])
                        pass
                    else:
                        pass
                    data=int(full[0].strip()[0])
                    street_address = full[0]
                    city = full[1].split(",")[0]
                    state = full[1].split(",")[1].split( )[0]
                    zipp = full[1].split(",")[1].split( )[1]
                    phone = full[3]
                except:
                    
                    street_address = full[1]
                    if link != None:
                        # print(link['href'])

                        ku = (link['href'].split("sll=")[-1].split("&sspn=")[0])
                        latitude = ku.split(",")[0].replace("http://goo.gl/maps/Hdejr","<MISSING>")
                        longitude =  ku.split(",")[-1].replace("http://goo.gl/maps/Hdejr","<MISSING>")
                        # print(longitude)
                        
                    if "Bronx River Medical Associates" in full:
                        pass
                    else:
                        if full[-1]=="Find on Google Maps":
                            del full[-1]
                        if "Phone:" in full:
                            location_name = full[0]
                            street_address =  full[1]

                            city = full[-3].split(",")[0]
                            state = full[-3].split(",")[1].split( )[0]
                            zipp = full[-3].split(",")[1].split( )[1]
                            phone = full[-1]
                        else:
                            location_name = " ".join(full[:-2])
                            street_address = full[-2]
                            city = full[-1].split(",")[0]
                            state =  " ".join(full[-1].split(",")[-1].split( )[:-1])
                            zipp = full[-1].split(",")[-1].split( )[-1]
                store = []
                store.append(base_url if base_url else "<MISSING>")
                store.append(location_name if location_name else "<MISSING>") 
                store.append(street_address if street_address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state.replace("New","New York").replace("York York","York")if state else "<MISSING>")
                store.append(zipp if zipp else "<MISSING>")
                store.append("US")
                store.append("<MISSING>") 
                store.append(phone if phone else "<MISSING>")
                store.append("<MISSING>")
                store.append(latitude if latitude else "<MISSING>")
                store.append(longitude if longitude else "<MISSING>")
                store.append("<MISSING>")
                store.append("<MISSING>")
                # store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                if store[2] in address :
                    continue
                address.append(store[2])
                yield store 
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
