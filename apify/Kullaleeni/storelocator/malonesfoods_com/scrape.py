#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 22:50:41 2019

@author: srek
"""

import requests
from bs4 import BeautifulSoup
from lxml import html
import pandas as pd

def fetch_data():

    url = "http://www.malonesfoods.com/"
    data = []
    page = requests.get(url)
    #soup = BeautifulSoup(page.text)
    tree = html.fromstring(page.content)
    
    record_list = ["/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div[2]/div/div/table/tbody/tr/td[2]/div[1]/strong//text()",
                   "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div[2]/div/div/table/tbody/tr/td[2]/div[3]/strong//text()",
                   "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div[2]/div/div/table/tbody/tr/td[2]/div[5]/strong//text()",
                   "/html/body/div[1]/div/div/div[2]/div[2]/div/div/div/div[2]/div/div[2]/div/div/table/tbody/tr/td[2]/div[8]/strong//text()"]
    
    
    for i in range(4):
        record = tree.xpath(record_list[i])[0].split("\xa0")  
        record = [r.strip() for r in record]
        record = list(filter(None, record))
        try:
            record.remove('Main Office')
        except:
            pass
        location_name = record[0]
        street_address =  record[1]
        city,[state,zipcode] =  record[2].split(",")[0].strip(),record[2].split(",")[1].strip().split(" ")
        phone = record[3]
        locator_domain = url
    
        country_code = "US"
        data_record = {}
        
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
        data_record['latitude'] = '<MISSING>'
        data_record['longitude'] = '<MISSING>'
        data_record['hours_of_operation'] = '<MISSING>'
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
        














