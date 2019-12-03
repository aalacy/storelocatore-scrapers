#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 15:27:17 2019

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
    url = "https://www.nygard.com/en-ca/LocateStore"
    locator_domain = url
    data = []
    driver = get_driver()
    driver.get(url)
    time.sleep(3)

    locateUnit = driver.find_element_by_id('locateUnit')
    for opt in locateUnit.find_elements_by_tag_name('option'):
        if opt.text == 'mi.':
            opt.click()
    locateRadius = driver.find_element_by_id('locateRadius')
    for opt in locateRadius.find_elements_by_tag_name('option'):
        if opt.text == '100':
            opt.click()
        
    
    el = driver.find_element_by_id('Province')
    for option in el.find_elements_by_tag_name('option'):
        if option.text != "Province / State":
            if option.text == "United States":
                country_code = "US"
            elif  option.text == "Canada":
                country_code = "CA"
            else:
                country_code = country_code
                
            option.click() # select() in earlier version
            time.sleep(1)
            driver.find_element_by_id("findStore").click()
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source)
            #noofstores = soup.find("div",attrs={"id":"store_count"}).text
            
            stores = soup.find("div",attrs={"id":"resultsList"}).find_all("div",attrs={"class":"storeResult row store-location"})
            stores = stores + soup.find("div",attrs={"id":"resultsList"}).find_all("div",attrs={"class":"storeResult row "})
            
            if stores == []:
                stores = soup.find_all("div",attrs={"class":"row store-location"})
                for s1 in range(len(stores)):
                    add1 = [a.strip() for a in stores[s1].text.split("\n")]
                    add1 =  list(filter(None,add1))
                    phone = add1[-1]
                    location_name = add1[0]
                    add1.remove(location_name)
                    p_list = []
                    for p in phone:
                        try:
                            if int(p) in [0,1,2,3,4,5,6,7,8,9]:
                                p_list.append(p)
                        except:
                            pass
                    
                    if len(p_list) < 9:
                        phone = '<MISSING>'
                    else:
                        add1.remove(phone)
                    
                    city,state = add1[-1].split(",")
                    add1.remove(add1[-1])
                    street_address = ','.join(add1)
                    zipcode = '<MISSING>'
                    location_type = '<MISSING>'
                    
                    data_record = {}
                    data_record['locator_domain'] = locator_domain.strip()
                    data_record['location_name'] = location_name.strip()
                    data_record['street_address'] = street_address.strip()
                    data_record['city'] = city.strip()
                    data_record['state'] = state.strip()
                    data_record['zip'] = zipcode.strip()
                    data_record['country_code'] = country_code
                    data_record['store_number'] = '<MISSING>'
                    data_record['phone'] = phone.strip()
                    data_record['location_type'] = location_type.strip()
                    data_record['latitude'] = '<MISSING>'
                    data_record['longitude'] = '<MISSING>'
                    data_record['hours_of_operation'] = '<MISSING>'
                    data_record['page_url'] = '<MISSING>'
                    data.append(data_record)
                    #print(len(data))
                    
            else:        
                for sss in range(len(stores)):
                    add_ph = stores[sss].text.split("\n")
                    add_ph = [a.strip() for a in add_ph]
                    add_ph =  list(filter(None,add_ph))
                    #print(add_ph)
                    p_list = []
                    phone = add_ph[-1]
                    for p in phone:
                        try:
                            if int(p) in [0,1,2,3,4,5,6,7,8,9]:
                                p_list.append(p)
                        except:
                            pass
                    
                    if len(p_list) < 9:
                        phone = '<MISSING>'
                    else:
                        add_ph.remove(phone)
                        
                    location_name = add_ph[0]
                    city_state = add_ph[-1]
                    add_ph.remove(location_name)
                    add_ph.remove(city_state)
                    try:
                        city,state = city_state.split(",")
                    except:
                        city,state = '<MISSING>','<MISSING>'
    
                    street_address =','.join(add_ph)
                    #if street_address == 'NAIN                , NL':
                        #print( list(filter(None,stores[sss].text.split("\n"))))
                    #    break
                    zipcode = '<MISSING>'
                    if "nyg" in location_name.lower():
                        location_type = "Nygard Stores"
                    else:
                        location_type = "Other Fine Retails"
                    
                        
                    data_record = {}
                    data_record['locator_domain'] = locator_domain.strip()
                    data_record['location_name'] = location_name.strip()
                    data_record['street_address'] = street_address.strip()
                    data_record['city'] = city.strip()
                    data_record['state'] = state.strip()
                    data_record['zip'] = zipcode.strip()
                    data_record['country_code'] = country_code
                    data_record['store_number'] = '<MISSING>'
                    data_record['phone'] = phone.strip()
                    data_record['location_type'] = location_type.strip()
                    data_record['latitude'] = '<MISSING>'
                    data_record['longitude'] = '<MISSING>'
                    data_record['hours_of_operation'] = '<MISSING>'
                    data_record['page_url'] = '<MISSING>'
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
    df_data.to_csv('./data.csv',index = 0,header=True,columns=['locator_domain','location_name','street_address','city',
                                                               'state','zip','country_code','store_number','phone','location_type',
                                                               'latitude','longitude','hours_of_operation','page_url'])

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

