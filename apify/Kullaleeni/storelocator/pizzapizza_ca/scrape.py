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
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
    driver.get(url)
    time.sleep(5)
    
    city_list = pd.read_csv("./CA_City_List.csv").City_State.tolist()
    
    for st in range(286,len(city_list),5):
        time.sleep(5)
        print(st)
        element = driver.find_element_by_id("name")
        element.clear()
        element.send_keys(city_list[st])
        
        try:
            driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div[3]/form/fieldset/div/input").click()
        except:
            #time.sleep(5)
            driver.get(url)
            #time.sleep(5)
            element = driver.find_element_by_id("name")
            element.clear()
            element.send_keys(city_list[st])
            try:
                driver.find_element_by_xpath("/html/body/div[1]/div[3]/div[1]/div[3]/form/fieldset/div/input").click()
            except:
                break
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source)
        time.sleep(2)
        if "No search" not in soup.find("div",attrs={"id":"location-section"}).text or "Please try again later" not in soup.find("div",attrs={"id":"location-section"}).text :
            #print(soup.find("div",attrs={"id":"location-section"}).text)
            
            try:
                noofpages = int(soup.find("div",attrs={"id":"pagel"}).find_all("li")[-1].text)
            except:
                noofpages = 1
            #print(noofpages)
            
            for n in range(2,noofpages):
                soup = BeautifulSoup(driver.page_source)
                
                store_list = soup.find_all("div",attrs={"class":"location-section"})
                
                for sl in range(len(store_list)):
                    street_address = store_list[sl].find("h3").text
                    address = store_list[sl].find("div",attrs={"class":"columnAddress"}).text.strip()
                    location_name = street_address
                    
                    city,state,zipcode = address.split(",")
                    
                    city = city.strip()
                    state = state.strip()
                    zipcode = zipcode.strip()
                    country_code = "CA"
                    location_type = "<MISSING>"
                    
                    phone = store_list[sl].find("div",attrs={"class":"column"}).find_all("dd")[1].text
                    hours_of_open = BeautifulSoup(str( store_list[sl].find("div",attrs={"class":"column hours"})).replace("</dd><dt>"," ; ")).text.strip().replace("  "," ")
                    
                    #try:
                    #    latitude,longitude = store_list[sl].find("div",attrs={"class":"button-holder"}).find("a",attrs={"class":"btn-directions"}).get("href").split("AX")[-2:]
                    #except:
                    latitude,longitude = "<MISSING>","<MISSING>"
                    
                    data_record = {}
                    
                    locator_domain = url
                    store_number = "<MISSING>"
                
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
                    data_out.append(data_record)
                    df_data = pd.DataFrame(columns=['locator_domain','location_name','street_address','city','state','zip','country_code','store_number','phone','location_type','latitude','longitude','hours_of_operation'])
                    
                    for d in range(len(data_out)):
                        df = pd.DataFrame(list(data_out[d].values())).transpose()
                        df.columns = list((data_out[d].keys()))   
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
                    df_data.to_csv('./data.csv',index = 0,header=True)
                
                
                driver.find_element_by_xpath('//*[@id="{0}"]'.format(n)).click()
                time.sleep(5)
       # except:
           # print(st)
            #pass               
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
    df_data.to_csv('./data.csv',index = 0,header=True)

def scrape():
    data = fetch_data()
    write_output(data)


scrape()



