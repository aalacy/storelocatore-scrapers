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

    base_url1="https://www.portcityjava.com/our-locations"
    r = requests.get(base_url1)
    soup1= BeautifulSoup(r.text,"lxml")
    site_rl=soup1.find("div",{"class":"col-md-5 col-md-offset-1"})
    link = site_rl.find_all('a')
    return_main_object =[]
    store_detail =[]
    store_name=[]
    latitude1=[]
    longitude1 =[]

    for a in link:
        r = requests.get("https://www.portcityjava.com"+a['href'])
        soup= BeautifulSoup(r.text,"lxml")
        info = soup.find_all("ul",{"id":"all-locations"})
        for i in info:
            
            spans = i.find_all("span",{"class":"name"})
            lan_logs = i.find_all("div",{"class":"visually-hidden hidden"})
            
            for lan_log in lan_logs:
                latitude1.append(list(lan_log.stripped_strings)[0])
                longitude1.append(list(lan_log.stripped_strings)[1])
                

            for span in spans:
                if "Leland" in span.text or "Raleigh" in span.text or "Wilmington" in span.text:
                    pass
                else:
                    store_name.append(span.text)

            p = i.find_all('p')
            for index,j in enumerate(p):
                tem_var=[]
                street_address = list(j.stripped_strings)[0]
                city = (list(j.stripped_strings)[1])
                state = (list(j.stripped_strings)[3])
                zipcode ="<MISSING>"
                phone  = (list(j.stripped_strings)[4])
                latitude = (latitude1[index])
                longitude =(longitude1[index])
                
                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("portcityjava")
                tem_var.append(latitude)
                tem_var.append(longitude)
                tem_var.append("<MISSING>")
                store_detail.append(tem_var)

        for i in range(len(store_name)):
            store = list()
            store.append("https://www.portcityjava.com")
            store.append(store_name[i])
            store.extend(store_detail[i])
            return_main_object.append(store)
        
        return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




