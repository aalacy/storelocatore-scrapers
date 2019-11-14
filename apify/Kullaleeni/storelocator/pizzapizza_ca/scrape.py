#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 22 12:24:11 2019

@author: srek
"""

import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time
#from selenium.webdriver.common.keys import Keys

def check_zip(x):
    #print(x)
    if len(x) == 4:
        
        y = "0"+str(x)
        #print (y)
    elif len(x) == 9 and str(x) !="<MISSING>":
        y = x[:5]
        #print(y)
    elif len(x) == 8 and str(x) !="<MISSING>":
        y = "0"+x[:4]
        #print(y)
    else:
        y = x
    
    return y



def phone_check(x):
    if x != "<MISSING>":
        #print(x)
        y = x.replace("-","").replace(".","").strip()
        if len(y) < 10:
            #print(x)
            y = "<MISSING>"
        else:
            y = x
    else:
        y = x
    return y
    
def fetch_data():

    url = "https://www.pizzapizza.ca/locations/"
    
    data_out = []
    driver = webdriver.Chrome("chromedriver")
    driver.get(url)
    time.sleep(3)
    try:
        driver.find_element_by_xpath("/html/body/ngb-modal-window/div/div/app-location-modal/div/div[1]/div/div[1]/i").click()
    except:
        pass
    
    soup = BeautifulSoup(driver.page_source)
    store_locations = soup.find("div",attrs={"class":"row store-city-list no-gutters"}).find_all("li")
    
    for p in range(len(store_locations)):
        page_link = "https://www5.pizzapizza.ca"+ store_locations[p].find("a").get("href")
        driver.get(page_link)
        time.sleep(3)
 
 
        soup_1 = BeautifulSoup(driver.page_source)
        if "No results found".lower() not in soup_1.text.lower():
            
            records = soup_1.find_all("div",attrs={"class":"row search-results-row"})
            for r in range(len(records)):
            
                location_name = records[r].find("h2",attrs={"class":"fw-normal"}).text.strip()
                street_address = location_name
                try:
                    city,state,zipcode = records[r].find("p").text.split(",")
                except:
                    city,state,zipcode = "<MISSING>","<MISSING>","<MISSING>"
             
                location_type = records[r].find("div",attrs={"class":"col-12 align-self-end"}).find("p").text.replace("Available:","").replace("\xa0", " ").strip()
                
                hours_list = records[r].find("div",attrs={"class":"col-12 col-lg-5 store-hours"}).find_all("div",attrs={"class":"row justify-content-end no-gutters days-break-down"})
                
                hours_of_open = [h.text.replace("y","y : ") for h in hours_list]
    
                city = city.strip()
                state = state.strip()
                zipcode = zipcode.strip()
                country_code = "CA"
                location_type = "<MISSING>"
                            
                latitude,longitude = "<MISSING>","<MISSING>"
                
                data_record = {}
                
                locator_domain = url
                store_number = "<MISSING>"
                phone = "<MISSING>"
                
                
                data_record['locator_domain'] = locator_domain
                data_record['location_name'] = location_name
                data_record['street_address'] = street_address
                data_record['city'] = city
                data_record['state'] = state
                data_record['zip'] = zipcode
                data_record['country_code'] = country_code
                data_record['store_number'] = store_number
                data_record['phone'] = phone   
                data_record['location_type'] = location_type
                data_record['latitude'] = latitude
                data_record['longitude'] = longitude
                data_record['hours_of_operation'] = " ".join(hours_of_open)
                data_record['page_url'] = page_link
                
                data_out.append(data_record)
    
                    
    return data_out

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
    state_check = {"US":["AL","AK","AZ","AR","AA","AE","AP","CA","CO","CT","DE","DC","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","UT","TX","VT","VA","WA","WV","WI","WY"],"CA":["AB","BC","MB","NB","NL","NT","NS","NU","ON","PE","QC","SK","YT"]}
    
    for sc in range(len(list(state_check.keys()))):
        df_data.loc[df_data['state'].isin(state_check[list(state_check.keys())[sc]]),"country_code"] = list(state_check.keys())[sc]
    
    df_data['zip'] = df_data['zip'].map(lambda x : check_zip(x))
    df_data["phone"] = df_data.phone.map(lambda x : phone_check(x))
    df_data.to_csv('./data.csv',index = 0,header=True,columns=['locator_domain','location_name','street_address','city',
                                                               'state','zip','country_code','store_number','phone','location_type',
                                                               'latitude','longitude','hours_of_operation','page_url'])

    #df_data.to_csv('./data.csv',index = 0,header=True)

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



