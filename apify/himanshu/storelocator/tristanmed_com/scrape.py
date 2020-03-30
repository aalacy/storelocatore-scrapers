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

    base_url = "http://tristanmed.com/locations"

    r = session.get(base_url)

    main_soup = BeautifulSoup(r.content,"lxml")
    store_detail = []
    store_name = []
    lat_log = []
    housr1 = []


    k  = main_soup.find_all("div",{"class":"caption"})
    for i in k:
        ds = ''
        a  = i.find('a',{'class':"btn btn-primary pi-btn-grey no-rounded"})
        r = session.get(a['href'])
        soup = BeautifulSoup(r.content,"lxml")
        lat_log1 = soup.find("a",{"class":"btn btn-lg pi-btn-default"})
        if len(lat_log1['href'].split("n/")[1].split('%20')) ==1:
            lat_log.append(lat_log1['href'].split("n/")[1].split('%20')[0].split( ))
        else:
            lat_log.append(lat_log1['href'].split("n/")[1].split('%20'))


        times = i.find_all('span',{'class':'pull-right'})
        
        for time in times:
            housr = list(time.stripped_strings)
            for  i  in housr:
                ds = ds +' '+ i
        housr1.append(ds)


    for index , i  in enumerate(k):
        temp_var = []
        store_name.append(i.h5.text)
        street_address = i.find('span',{'itemprop':'streetAddress'}).text
        city = i.find('span',{'itemprop':'addressLocality'}).text
        state = i.find('span',{'itemprop':'addressRegion'}).text
        zipcode = i.find('span',{'itemprop':'postalCode'}).text
        phone = i.find('span',{'itemprop':'telephone'}).text

        temp_var.append(street_address)
        temp_var.append(city)
        temp_var.append(state)
        temp_var.append(zipcode)
        temp_var.append("US")
        temp_var.append("<MISSING>")
        temp_var.append(phone)
        temp_var.append("tristanmed")
        temp_var.append(lat_log[index][0].split(',')[0])
        temp_var.append(lat_log[index][1])
        temp_var.append(housr1[index])
        store_detail.append(temp_var)

    return_main_object = []
    for i in range(len(store_name)):
        store = list()
        store.append("http://tristanmed.com")    
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)


    return return_main_object
    

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
