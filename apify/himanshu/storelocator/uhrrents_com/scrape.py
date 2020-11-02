# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json,urllib
import time


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://uhrrents.com/locations/"
    r = session.get(base_url)

    soup = BeautifulSoup(r.content,"lxml")


    return_main_object = []

    k = soup.find('div',{"id":"locationResults"})
    store_name=[]
    k1=[]
    data1 =  k.find_all('li')
    hours = soup.find('div',{"class":"store-hours"})
    store_detail = []
    k1.append(hours.text.replace('\n',' '))
    for i in data1:
        tem_var=[]
        data = list(i.stripped_strings)
        name =data[0]
        store_name.append(name)

        street_address =data[1].split(',')[0]
        city = data[1].split(',')[1]
        state = data[1].split(',')[2].split( )[0]
        zipcode = data[1].split(',')[2].split( )[1]
        phone = data[2]
        hours_of_operation = k1[0]
        tem_var.append(street_address)
        tem_var.append(city)
        tem_var.append(state)
        tem_var.append(zipcode)
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("uhrrents")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(k1[0])
        store_detail.append(tem_var)


        
    for i in range(len(store_name)):
        store = list()
        store.append('http://uhrrents.com/')
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)

    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
