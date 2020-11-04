import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time 

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
    base_url = "https://www.chezcora.com"
    location_url = "https://www.chezcora.com/en/breakfast-restaurants"
    r = request_wrapper(location_url,"get",headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    data = soup.find("select",{"id":"provinces"}).find_all("option")
    for i in data:
        k = (i['value'][1:].lstrip().rstrip().strip())
        link = "https://www.chezcora.com/"+str(k)
        r1 = request_wrapper(link,"get",headers=headers)
        soup1 = BeautifulSoup(r1.text,"lxml")
        data1 = soup1.find_all("div",{"class":"col-1-2 resto-contact"})
        for i in data1:
            location_name = (i.find("h2").text.replace("é","e").replace("è","e").replace("â","a").replace("ô","o"))
            url = i.find("h2").find("a")['href']
            street_address = " ".join(i.find("p").text.split('<br/>')).split("\n\t\t\t\t\t\t\t\t\t\t")[1].replace("é","e").replace("è","e").replace("â","a").replace("ô","o")
            city =  " ".join(i.find("p").text.split('<br/>')).split("\n\t\t\t\t\t\t\t\t\t\t")[2].split(",")[0].replace("é","e").replace("è","e").replace("â","a").replace("ô","o")
            state = " ".join(i.find("p").text.split('<br/>')).split("\n\t\t\t\t\t\t\t\t\t\t")[2].split(",")[1].strip().rstrip().lstrip()
            zipp = " ".join(i.find("p").text.split('<br/>')).split("\n\t\t\t\t\t\t\t\t\t\t")[2].split(",")[2:][0].strip().rstrip().lstrip()
            phone = i.find_all("p")[1].text.replace("      ","")
            hours = (i.find("div",{"class":"tabHoraire"}).text.strip().lstrip().rstrip().replace("\n","").split(" "))
            hours_of_operation = " ".join(hours).replace("\n","").replace("\t","").replace("\r","").strip().replace("p.m.Saturday","p.m. Saturday").replace("p.m.Sunday","p.m. Sunday")
            page_url = ("https://www.chezcora.com"+str(url))
            r2 = request_wrapper(page_url,"get",headers=headers)
            soup2 = BeautifulSoup(r2.text,"lxml")
            data2 = soup2.find_all("script")[8]
            try:
                latitude = (data2.text.strip().lstrip().rstrip().split("bounds.push({")[1].split("icon")[0].split(",")[0].split("lat: ")[1])
                longitude = (data2.text.strip().lstrip().rstrip().split("bounds.push({")[1].split("icon")[0].split(",")[1].split("lon: ")[1])
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            store = []
            store.append(base_url if base_url else "<MISSING>")
            store.append(location_name if location_name else "<MISSING>") 
            store.append(street_address if street_address else "<MISSING>")
            store.append(city if city else "<MISSING>")
            store.append(state if state else "<MISSING>")
            store.append(zipp if zipp else "<MISSING>")
            store.append("CA")
            store.append("<MISSING>") 
            store.append(phone if phone else "<MISSING>")
            store.append("<MISSING>")
            store.append(latitude if latitude else "<MISSING>")
            store.append(longitude if longitude else"<MISSING>")
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
