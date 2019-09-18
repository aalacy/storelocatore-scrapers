#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 12 11:22:27 2019

@author: srek
"""
import pandas as pd
import re
import requests
from bs4 import BeautifulSoup

def string_clean(record):
    return record.replace("\r","").replace("\n","").strip()

def contact_info(address):
    phone = []
    remove_from_address = []
    
    for ad in range(len(address)):
        try:
            phone.append(re.search('\d{3}.\d{3}.\d{4}',address[ad]).group(0))  
            remove_from_address.append(address[ad])
            
        except:
            pass
        
    if phone == []:
        for ad in range(len(address)):
            try:
                phone.append(re.compile(r'(\(\d\d\d\)) (\d\d\d-\d\d\d\d)').search(address[ad]).group(0))
                remove_from_address.append(address[ad])
            except:
                pass
    

    email = []
    for ad in range(len(address)):
        if "email" in address[ad].lower():
            try:
                email.append(address[ad])
                remove_from_address.append(address[ad])
            except:
                pass
            
    return phone,email,remove_from_address

def fetch_data():

    url = "https://www.shakeshack.com/locations/"
    
    
    page = requests.get(url)
    
    
    soup = BeautifulSoup(page.text,"html.parser")
    
    locator_domain = url
    us_locations = soup.find_all("div",attrs={"class":"citys span10 offset1"})[0]
    
    
    states = [string_clean(x.text) for x in us_locations.find_all("h3")]
    
    data = []
    print(states)
    for s in range(len(states)):
        
        state = states[s]
        stores = us_locations.find("div",attrs={"id":"usa_{}".format(state.replace(" ","_"))}).find_all("div",attrs={"class":"row-fluid"})
        
        for st in range(len(stores)): 
            #print(s,st)
            location_name = stores[st].find("h4").text
            
            address = stores[st].find("div",attrs={"class":"address"}).text.replace("\xa0"," ").split("\n")
         
            data_record = {}
            #print(address)
            data_record['locator_domain'] = locator_domain
            data_record['location_name'] = location_name
            
            phone,email,remove_from_address = contact_info(address)    
            #[address.remove(e) for e in email]
            
            
            [address.remove(p) for p in remove_from_address]
            
            address = list(filter(None, address))
            address = ','.join(address).split(",")  
            try:
                zipcode = re.search('\d{5}',address[-1]).group(0)
            except:
                zipcode = "<MISSING>"
                
            
            
            city = ','.join(location_name.split(",")[:-1])
            street_address = ""
            for c in range(len(address)):
                if city in address[c]:
                    street_address = ','.join(address[:c])
            if street_address == "":
                if (zipcode == "<MISSING>") & (len(address) ==2):
                    city = address[1]
                    street_address = address[0]
                elif (zipcode == "<MISSING>") & (len(address) ==1):
                    street_address = address[0]
                    city = "<MISSING>" 
                else:
                    street_address = address[0]
                    
            country_code = "US"
            hours_of_open = (stores[st].find("div",attrs={"class":"opening"}).text.split('\n'))
            #print(hours_of_open)
            hours_of_open = ';'.join(list(filter(None, hours_of_open)))
            #print(hours_of_open)
            
            if state == "Washington, D.C." or state == "Washington DC": 
                state = "Washington"

            data_record['street_address'] = street_address
            data_record['city'] = city
            data_record['state'] = state
            data_record['zip'] = zipcode
            data_record['country_code'] = country_code
            data_record['store_number'] = '<MISSING>'
            try:
                data_record['phone'] = phone[0]   
            except:
                data_record['phone'] = '<MISSING>'
                
            data_record['location_type'] = '<MISSING>'
            data_record['latitude'] = '<MISSING>'
            data_record['longitude'] = '<MISSING>'
            data_record['hours_of_operation'] = hours_of_open
            data.append(data_record)
    return data

def write_output(data):
    df_data = pd.DataFrame(columns=['locator_domain','location_name','street_address','city','state','zip','country_code','store_number','phone','location_type','latitude','longitude','hours_of_operation'])
    
    for d in range(len(data)):
        df = pd.DataFrame(list(data[d].values())).transpose()
        df.columns = list((data[d].keys()))   
        df_data = df_data.append(df)
    #df_data = df_data.fillna("<MISSING>")
    df_data = df_data.replace(r'^\s*$', "<MISSING>", regex=True)
    df_data = df_data.drop_duplicates(["location_name","street_address"])
    df_data['zip'] = df_data.zip.astype(str)

    df_data.to_csv('./data.csv',index = 0,header=True)

def scrape():
    data = fetch_data()
    write_output(data)


scrape()






































