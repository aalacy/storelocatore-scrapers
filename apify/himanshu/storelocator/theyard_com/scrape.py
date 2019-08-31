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
  
    base_url= "https://theyard.com/new-york-city-coworking-office-space/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
  
    hours = []
    name_store=[]
    store_detail=[]
    phone=[]
    return_main_object=[]
    k=(soup.find_all("ul",{"class":"main-nav"}))

    for i in k:
        p = i.find_all("li")
        for p1 in p:
            if "Boston" in p1.a.text or "New York City" in p1.a.text or  "Washington, D.C." in p1.a.text or "Philadelphia" in p1.a.text:

                if "https://theyard.com/philadelphia-coworking-office-space/center-city/" in p1.a['href'] or "https://theyard.com/boston-coworking-office-space/back-bay" in p1.a['href']:
                    pass
                else:
                    # print(p1.a['href'])
                    base_url1= p1.a['href']
                    r = requests.get(base_url1)
                    soup1= BeautifulSoup(r.text,"lxml")
                    # print(soup1)
                    st1 = soup1.find_all("ul",{"class":"post-list map-info"})

                    for i in st1:
                        l = i.find_all("li")
                        for  j in l:
                            zip1=''
                            tem_var=[]
                            name = list(j.stripped_strings)[0]
                            st = list(j.stripped_strings)[3].split(",")[0]
                            city = list(j.stripped_strings)[3].split(",")[1]
                            state = list(j.stripped_strings)[3].split(",")[2].split( )[0]

                            if len(list(j.stripped_strings)[3].split(",")[2].split( ))==2:
                                zip1 = list(j.stripped_strings)[3].split(",")[2].split( )[-1]
                            
                            else:
                                zip1 = "<MISSING>"
                            
                            name_store.append(name)
                            tem_var.append(st)
                            tem_var.append(city)
                            tem_var.append(state)
                            tem_var.append(zip1)
                            tem_var.append("US")
                            tem_var.append("<MISSING>")
                            tem_var.append("<MISSING>")
                            tem_var.append("theyard")
                            tem_var.append("<MISSING>")
                            tem_var.append("<MISSING>")
                            tem_var.append("<MISSING>")
                            store_detail.append(tem_var)
                            
  
 
    
    for i in range(len(name_store)):
        store = list()
        store.append("https://theyard.com")
        store.append(name_store[i])
        store.extend(store_detail[i])
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

