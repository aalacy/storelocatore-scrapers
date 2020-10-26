#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 21:43:29 2019

@author: srek
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sweetfactorycandy_ca')



def fetch_data():
    url = "http://sweetfactorycandy.ca/"
    
    locator_domain = url
    
    page = requests.get(url)
    soup = BeautifulSoup(page.text,"html.parser")
    
    phone = soup.find("li",attrs={"class":"phone"}).text.replace("Phone","")
    address = BeautifulSoup(str(soup.find("li",attrs={"class":"address"})).split("br")[0]).text.replace("Address","").replace("The Sweet Factory:","").replace("\n","").replace("\t","").strip()
    
    hours_of_open = BeautifulSoup(''.join(str(soup.find("li",attrs={"class":"address"})).split("br")[1:])).text.replace(">","").replace("<","").replace("\r\n",";").split("Map")[0].replace("\t","").replace("\n","").strip()[1:]
    city = address.split(",")[0].split(" ")[-1]
    street_address = address.split(",")[0].replace(city,"").strip()
    
    state = address.split(",")[1].strip().split(" ")[0]
    zipcode = address.split(",")[1].strip().replace(state,"").strip().replace(".","")
    
    data_record = {}
    #logger.info(address)
    data_record['locator_domain'] = locator_domain
    data_record['location_name'] = '<MISSING>'
    
    country_code = "CA"
    
    
    data_record['street_address'] = street_address
    data_record['city'] = city
    data_record['state'] = state
    data_record['zip'] = zipcode
    data_record['country_code'] = country_code
    data_record['store_number'] = '<MISSING>'
    data_record['phone'] =phone  
    data_record['location_type'] = '<MISSING>'
    data_record['latitude'] = '<MISSING>'
    data_record['longitude'] = '<MISSING>'
    data_record['hours_of_operation'] = hours_of_open
    
    return data_record


def write_output(data):
    df_data = pd.DataFrame(columns=['locator_domain','location_name','street_address','city','state','zip','country_code','store_number','phone','location_type','latitude','longitude','hours_of_operation'])
    
    #for d in range(len(data)):
    df = pd.DataFrame(list(data.values())).transpose()
    df.columns = list((data.keys()))   
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



