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
    base_url= "https://lostpizza.com/locations/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]

    data = soup.find_all("div",{"class":"location-box"})
    for i in data:
        store_name.append(list(i.h1.stripped_strings)[0])
        tem_var =[]
        street_address = list(i.stripped_strings)[1]
        city = list(i.stripped_strings)[2].split(',')[0]
        state=list(i.stripped_strings)[2].split(',')[1].split( )[0]
        zipcode  = list(i.stripped_strings)[2].split(',')[1].split( )[1]
        phone =  list(i.stripped_strings)[3]
        v =list(i.stripped_strings)
        v.pop(0)
        v.pop(0)
        v.pop(0)
        v.pop(0)
        hours = "  ".join(v)
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipcode)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("lostpizza")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours)
        store_detail.append(tem_var)        

        
    for i in range(len(store_name)):
        store = list()
        store.append("https://lostpizza.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
