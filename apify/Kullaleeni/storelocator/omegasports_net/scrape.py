#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 11:14:17 2019

@author: srek
"""

from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.chrome.options import Options

def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)

def fetch_data():
    
    url = "https://www.omegasports.com/store_locations.cfm"
    
    locator_domain = url
    
    driver = get_driver()
    driver.get(url)
    soup = BeautifulSoup(driver.page_source,"html.parser")
    data = []
    
    records = soup.find("div",attrs={"class":"store-loc-container"}).find_all("div",attrs={"class":"storeContainer"})
    
    
    for r in range(len(records)):
        data_record = {}
        location_name = records[r].find("h5").text
        latitude,longitude = records[r].find("h4")["onclick"].replace("changeMap(","").replace(");","").split(",")[1:]
        city,state =  records[r].find("h4").text.replace("\n","").replace("\t","").strip().split(",")
        zipcode = records[r].find("p").text.split(" ")[-1]
        zipcode = zipcode.strip()
        city = city.strip()
        state = state.strip()
        
        street_address = (records[r].find("p").text.replace(zipcode,"").strip()+" "+records[r].find_all("p")[1].text).strip()
        
        phone = records[r].find("a").text
        hours_of_open = '<MISSING>'
        country_code = "US"
        
        data_record['locator_domain'] = locator_domain
        data_record['location_name'] = location_name
        data_record['street_address'] = street_address
        data_record['city'] = city
        data_record['state'] = state
        data_record['zip'] = zipcode
        data_record['country_code'] = country_code
        data_record['store_number'] = '<MISSING>'
        data_record['phone'] = phone   
        data_record['location_type'] = '<MISSING>'
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
















