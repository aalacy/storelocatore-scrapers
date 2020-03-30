import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

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
    base_url1="https://baldinos.us/locations/"
    r = session.get(base_url1)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    k= soup.find_all("div",{"class":"et_pb_text_inner"})

    for i in k:
        phone=''
    
        p = i.find_all('p')
        h = i.find_all('h3')
        for h1 in h:
            # if "Augusta" in h1.text:
            store_name.append(h1.text)

        for p1 in p:
            tem_var=[]
            if len(list(p1.stripped_strings)) ==2:
                street_address = list(p1.stripped_strings)[0].split(',')[0]
                city = list(p1.stripped_strings)[0].split(',')[1]
                state =  list(p1.stripped_strings)[0].split(',')[2].split( )[0]
                zipcode = list(p1.stripped_strings)[0].split(',')[2].split( )[1]
                phone1 = list(p1.stripped_strings)[1]
                if "CLOSED FOR REMODELING…REOPENING SUMMER 2019" in phone1:
                    phone = "<MISSING>"
                else:
                    phone = phone1
            else:
                street_address = list(p1.stripped_strings)[0].split(',')[0]
                city = list(p1.stripped_strings)[0].split(',')[1]
                state = list(p1.stripped_strings)[0].split(',')[2].split( )[0]
                zipcode = list(p1.stripped_strings)[0].split(',')[2].split( )[1]
                phone = list(p1.stripped_strings)[1]
            
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("baldinos")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            store_detail.append(tem_var)        
    store_name.insert(3,"Augusta") 
    store_name.insert(7,"Pooler")   
    store_name.insert(10,'Savannah') 
    store_name.insert(11,'Savannah') 
    
    for i in range(len(store_name)):
        store = list()
        store.append("https://baldinos.us")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

