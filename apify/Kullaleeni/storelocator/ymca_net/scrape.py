#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 26 02:57:42 2019

@author: srek
"""

import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)

def fetch_data():
    data = []
    driver = get_driver()
        
    df_zips = pd.read_csv("./US_states.csv")["Zip_Range"].tolist()
    for z in range(len(df_zips)):
        try:
            min_z,max_z = df_zips[z].split("-")
            min_z = int(min_z.strip())
            max_z = int(max_z.strip())
            if max_z - min_z <= 100:
                zip_lookup = range(min_z,max_z,10)
            else:
                zip_lookup = range(min_z,max_z,50)
                
        except:
            zip_lookup = [int(df_zips[z])]
        
        for lookupzip in zip_lookup:
            #print(lookupzip)
            locator_domain =  "https://www.ymca.net"
            url = "https://www.ymca.net/find-your-y/?address={}".format(lookupzip)
            driver.get(url)
            time.sleep(3)
        
            soup = BeautifulSoup(driver.page_source)
            pages = soup.find_all("ul",attrs={"class":"find-y-page"})
            
            for p in range(len(pages)):
               # print(pagenumber)
                try:
                    stores = pages[p].find_all("li")
                    
                    for s in range(len(stores)):
                        #print(p,len(stores))
                        #latitude = stores[s]['data-latitude']
                        #longitude = stores[s]['data-longitude']
                        location_name = stores[s].find("span",attrs={"class":"info-window-heading"}).text
                        location_link = "https://www.ymca.net" + stores[s].find("span",attrs={"class":"info-window-heading"}).find("a").get("href")
                        
                        add_ph =  list(filter(None,stores[s].find("span",attrs={"class":"info-window-body"}).text.replace("\n","").split("                    ")))
                        add_ph = [i.strip() for i in add_ph]
                        if "phone" in add_ph[-1].lower():
                            phone = add_ph[-1]
                        add_ph.remove(phone)
                        city,[state,zipcode] = add_ph[-1].strip().split(",")[0],  add_ph[-1].strip().split(",")[1].strip().split(" ")
                        add_ph.remove(add_ph[-1])
                        street_address = ",".join(add_ph).strip()
                        
                        driver.get(location_link)
                        time.sleep(2)
                        soup_loc = BeautifulSoup(driver.page_source)
                        lat_lon = soup_loc.find("div",attrs={"id":"y-profile-position"})
                        
                        latitude = lat_lon["data-latitude"]
                        longitude = lat_lon["data-longitude"]
                        #print(city)
                        p_list  = soup_loc.find_all("p")
                        hours_of_operation = [p.text for p in p_list if "Hours of Operation:".lower() in p.text.lower()]
                        hours_of_operation = [h.strip() for h in hours_of_operation[0].split("\n") if h.strip() != ""]
                        
                        store_number = location_link.split("id=")[1]

                        country_code = "US"
                        data_record = {}
                        data_record['locator_domain'] = locator_domain
                        data_record['location_name'] = location_name
                        data_record['street_address'] = street_address
                        data_record['city'] = city
                        data_record['state'] = state
                        data_record['zip'] = zipcode
                        data_record['country_code'] = country_code
                        data_record['store_number'] = store_number
                        data_record['phone'] = phone   
                        data_record['location_type'] = '<MISSING>'
                        data_record['latitude'] = latitude
                        data_record['longitude'] = longitude
                        data_record['hours_of_operation'] = ",".join(hours_of_operation)
                        data_record['page_url'] = location_link
                        data.append(data_record)
                        #print(len(data))
            
                except:
                    pass
            
            
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

    df_data.to_csv('./data.csv',index = 0,header=True,columns=['locator_domain','location_name','street_address','city',
                                                               'state','zip','country_code','store_number','phone','location_type',
                                                               'latitude','longitude','hours_of_operation','page_url'])

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
   
            
        
        
        
        
        
        
        
        
        
