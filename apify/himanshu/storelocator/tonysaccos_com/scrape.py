import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    base_url= "https://tonysaccos.com/locations/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone1=[]
    st1 =[]
    city =[]
    zipcode =[]
    state=[]
    hours1=[]
    latitude =[]
    longitude =[]
    data = soup.find_all("div",{"class":"locations_scroll"})
    
    for i in data:
        names = i.find_all("span",{"itemprop":"name"})
        phone  = i.find_all("span",{"itemprop":"telephone"})
        std = i.find_all("span",{"itemprop":"streetAddress"})
        hours = i.find_all("div",{"class":"hours"})
        links = i.find_all("div",{"class":"links"})
        for n in names:
            store_name.append(n.text)
      
        for p in phone:
            phone1.append(p.text)
        
        for st in std:
            st1.append(st.text.split(',')[0])
            city.append(st.text.split(',')[1].split( )[0])
            state.append(st.text.split(',')[1].split( )[1])
            zipcode.append(st.text.split(',')[1].split( )[2])
            
        for h in hours:
            hours1.append(h.text)
         
        for l in links:
            latitude.append(l.a['href'].split("/")[5].split(',')[0])
            longitude.append(l.a['href'].split("/")[5].split(',')[1])
    for i in range(len(store_name)):
        store = list()
        store.append("https://tonysaccos.com")

        store.append(store_name[i])
        store.append(st1[i])
        store.append(city[i])
        store.append(state[i])
        store.append(zipcode[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone1[i])
        store.append("tonysaccos")
        store.append(latitude[i])
        store.append(longitude[i])
        store.append(hours1[i])
        return_main_object.append(store)
        
        
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

