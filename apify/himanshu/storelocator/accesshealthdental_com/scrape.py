# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json,urllib
import time
import lxml


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
    base_url = "https://www.accesshealthdental.com/locations/"

    r = session.get(base_url )
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object=[]
    store_names = []
    store_detail =[]
    latitude =[]
    longitude =[]

    k = soup.find("div",{"class":"su-tabs su-tabs-style-default"})
    name1 =k.find_all("div",{"class":"su-tabs-pane su-clearfix"})
    for  i in name1:
        store_names.append(i.h2.text) 

    p = k.find_all('p')
    lat_log1 = soup.find_all("div",{"class":"video-container"})

    for i in lat_log1:
        if len(i.iframe.get('src').split('3d')) != 1:
            latitude.append(i.iframe.get('src').split('3d')[1].split('!2')[0])
            longitude.append(i.iframe.get('src').split("!2d")[1].split('!3d')[0])



    for index,i in  enumerate(p):
        temp_var =[]
        data = list(i.stripped_strings)
        if len(data) ==7:
            street_address = data[5]
            city_zip = data[6]
            city = city_zip.split(',')
            if len(city) ==1:
                state = city[0].split( )[2]
                zipcode =  city[0].split( )[3]
                city = city[0].split( )[0] + ' ' +city[0].split( )[1]        
            else:
                state = city[1].split( )[0]
                zipcode  = city[1].split( )[1]
                city = city[0]

            phone = data[1]

            temp_var.append(street_address)
            temp_var.append(city)
            temp_var.append(state)
            temp_var.append(zipcode)
            temp_var.append("US")
            temp_var.append("<MISSING>")
            temp_var.append(phone)
            temp_var.append("accesshealthdental")
            store_detail.append(temp_var)
        
        else:
            if len(data) != 4:
                street_address = data[4]
                city_zip = data[5].split(',')
                city =  data[5].split(',')[0]
                state = data[5].split(',')[1].split( )[0]
                zipcode =  data[5].split(',')[1].split( )[1]
                phone = data[1]

                temp_var.append(street_address)
                temp_var.append(city)
                temp_var.append(state)
                temp_var.append(zipcode)
                temp_var.append("US")
                temp_var.append("<MISSING>")
                temp_var.append(phone)
                temp_var.append("accesshealthdental")
                store_detail.append(temp_var)


    for i in  range(len(store_names[2:])):
        store = list()
        store.append("https://www.accesshealthdental.com")
        store.append(store_names[i+2])
        store.extend(store_detail[i])
        store.append(latitude[i])
        store.append(longitude[i])
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object
    



def scrape():
    data = fetch_data()
    write_output(data)

scrape()
