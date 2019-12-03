#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 16:58:58 2019

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
    #df_ca_list = pd.read_csv("/home/srek/xyz/Odetta/CA_states.csv")
    driver = get_driver()

    data = []
    
    #states_list = df_ca_list.State.drop_duplicates().tolist()
    state_list = ["Alberta, CA","British Columbia, CA","Manitoba, CA","New Brunswick, CA","Newfoundland and Labrador, CA","Northwest Territories, CA","Nova Scotia, CA","Nunavut, CA","Ontario, CA","Prince Edward Island, CA","Quebec, CA","Saskatchewan, CA","Yukon, CA"]
    for i in range(len(state_list)):
        print (i)
        #df_cities = df_ca_list.loc[df_ca_list.State == states_list[ca]].City_State.drop_duplicates().tolist()
        #if len(df_cities) >= 50:
        #    gap = 10
        #else:
        #    gap = 5        
        #        
        #for i in range(0,len(df_cities),gap):
        zip_lookup = state_list[i] 
        url = "https://www.medicineshoppe.ca/en/find-a-store?ad={}".format(zip_lookup.replace(" ","+").replace(",","%2C"))

        locator_domain = "medicineshoppe.ca"
        
        driver.get(url)
        time.sleep(5)

        driver.find_element_by_class_name("search-button").click()
        time.sleep(5)

        soup = BeautifulSoup(driver.page_source,"html.parser")
        
        store_list = soup.find("ul",attrs={"class":"search-list"}).find_all("li",attrs={"class":"banner-m"})
        
        for st in range(len(store_list)):
            data_record = {}
    
            location_name = BeautifulSoup(str(store_list[st].find("div",attrs={"class":"phamacist-name "})).split('<span class="distance">')[0]).text
            try:
                store_number = location_name.split("#")[1]
            except:
                store_number = "<MISSING>"

            location_type = store_list[st].find_all("span",attrs={"class":"tags"})  
            
            if location_type  == []:
                location_type = store_list[st].find_all("span",attrs={"class":"open-tag closed"})
            location_type = ','.join([lt.text for lt in location_type])
            address = store_list[st].find("address").text.split(",")
            
            if len(address) == 4:
                street_address,city,state,zipcode = address
            state = state.replace("(","").replace(")","").strip()
            city = city.strip()
            street_address = street_address.strip()
            zipcode = zipcode.strip()
            
            
            store_link = "https://www.medicineshoppe.ca" + store_list[st].find("a",attrs={"class":"details"}).get("href")
            
            driver.get(store_link)  
            time.sleep(5)
            
            soup_1 = BeautifulSoup(driver.page_source,"html.parser")
            
            
            try:
                phone = soup_1.find("div",attrs={"class":"columns medium-12 large-6 pharmacy-content-infos"}).find("a").text
            except:
                phone = "<MISSING>"
            hours_of_open = soup_1.find("div",attrs={"class":"table-hours-container"}).find_all("tr")
            
            for t in range(len(hours_of_open)):
                hours_of_open[t] = ' : '.join([h.text for h in hours_of_open[t].find_all("td")])
            hours_of_open = " ;".join(hours_of_open)
            latitude , longitude = store_list[st].find("a",attrs={"class":"direction"}).get("href").split("daddr=")[1].split(",")
            country_code = "CA"
            
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








    
