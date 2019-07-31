# -*- coding: utf-8 -*-
import csv
import requests
from bs4 import BeautifulSoup
import re
import json,urllib
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://www.sappbros.net/petroleum/locations/"

    r = requests.get(base_url)

    soup = BeautifulSoup(r.text,"lxml")

    return_main_object = []
    k = soup.find_all('div',{'class':'address'})

    store_name =[]
    store_detail =[]
    for i in k:
        temp =[]
        store_name.append(i.h2.text)
        data = list(i.ul.stripped_strings)
        for j in data:
            temp_var=[]
            if 'Phone' in j or ':' in j or 'Toll free' in j or 'Show on map' in j or 'Fax' in j:
                pass
            else:
                temp.append(j)
        street_address = (temp[0])
        city =''
        zipcode=''
        phone =''
        if len(temp[1].split(',')) == 2:
            city = temp[1].split(',')[0]
            state =  temp[1].split(',')[1].split( )[0]
            zipcode =  temp[1].split(',')[1].split( )[1]
        else:
            city = '<MISSING>'
            state =  temp[1].split( )[0]
            zipcode =  temp[1].split( )[1]
        phone = temp[2] 
     
        
        temp_var.append(street_address)
        temp_var.append(city)
        temp_var.append(state)
        temp_var.append(zipcode)
        temp_var.append("US")
        temp_var.append("<MISSING>")
        temp_var.append(phone)
        temp_var.append("sappbros")
        temp_var.append("<MISSING>")
        temp_var.append("<MISSING>")
        temp_var.append("<MISSING>")
        store_detail.append(temp_var)


    for i in range(len(store_name)):
        store = list()
        store.append("http://www.sappbros.net")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
