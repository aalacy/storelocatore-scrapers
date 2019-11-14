#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 29 20:33:11 2019

@author: srek
"""
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time


def fetch_data():
    url = "https://firstmidwest.com/locations/"
    locator_domain = url
    data = []
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(10)
    
    df_zip = pd.read_csv("US_states.csv")
    
    states = df_zip.State_Mod.drop_duplicates().tolist()
    
    for s in range(len(states)):
        try:
            driver.find_element_by_xpath("//select/option[@value='100']").click()
            element = driver.find_element_by_xpath('//*[@id="rio-txbCityState"]')
            element.clear()
            element.send_keys(states[s])
            driver.find_element_by_xpath('//*[@id="rio-searchZip"]').click()
            time.sleep(3)
            
            driver.find_element_by_xpath('//*[@id="spid17549"]').click()
            time.sleep(2)
            driver.find_element_by_xpath('//*[@id="spid17551"]').click()
            time.sleep(2)
            driver.find_element_by_xpath('//*[@id="spid17553"]').click()
            time.sleep(2)
            driver.find_element_by_xpath('//*[@id="spid17555"]').click()
            time.sleep(2)
            driver.find_element_by_xpath('//*[@id="spid17601"]').click()
            time.sleep(2)
            
            driver.find_element_by_xpath('//*[@id="spid17549"]').click()
            time.sleep(2)
            
            soup_page = BeautifulSoup(driver.page_source)
            if "We're sorry there are no locations" in soup_page.find("div",attrs={"id":"rio-listWrapper"}).text:
                driver.find_element_by_xpath('//*[@id="spid17549"]').click()
                time.sleep(2)
                pass
            else:
                soup_page = BeautifulSoup(driver.page_source)
            
                records = soup_page.find_all("div",attrs={"id":"rio-listWrapper"})
                for r in range(len(records)):
                    location_name = records[r].find("strong").text + ", " + records[0].find_all("strong")[1].text
                    street_address = records[r].find("div",attrs={"class":"rio-list-addr"}).text 
                    add = records[r].find("div",attrs={"class":"rio-list-csz"}).text
                    try:
                        city,[state,zipcode] = add.split(",")[0],add.split(",")[1].strip().split(" ")
                    except:
                        city,[state,zipcode] = add,[add,add]
                    country_code = "USA"
                    location_type = soup_page.find("label",attrs={"for":"spid17601"}).text.split("[")[0].strip()
                    phone = '<MISSING>'
                    
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
                    
                driver.find_element_by_xpath('//*[@id="spid17549"]').click()
                time.sleep(2)
            
            driver.find_element_by_xpath('//*[@id="spid17551"]').click()
            time.sleep(2)
            soup_page = BeautifulSoup(driver.page_source)
            if "We're sorry there are no locations" in soup_page.find("div",attrs={"id":"rio-listWrapper"}).text:
                driver.find_element_by_xpath('//*[@id="spid17551"]').click()
                time.sleep(2)
            else:   
                soup_page = BeautifulSoup(driver.page_source)
            
                records = soup_page.find_all("div",attrs={"id":"rio-listWrapper"})
                for r in range(len(records)):
                    location_name = records[r].find("strong").text + ", " + records[0].find_all("strong")[1].text
                    street_address = records[r].find("div",attrs={"class":"rio-list-addr"}).text 
                    add = records[r].find("div",attrs={"class":"rio-list-csz"}).text
                    try:
                        city,[state,zipcode] = add.split(",")[0],add.split(",")[1].strip().split(" ")
                    except:
                        city,[state,zipcode] = add,[add,add]
                    country_code = "USA"
                    location_type = soup_page.find("label",attrs={"for":"spid17601"}).text.split("[")[0].strip()
                    phone = '<MISSING>'
                    
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
                    
                driver.find_element_by_xpath('//*[@id="spid17551"]').click()
                time.sleep(2)
           
            
            driver.find_element_by_xpath('//*[@id="spid17553"]').click()
            time.sleep(2)
            soup_page = BeautifulSoup(driver.page_source)
            if "We're sorry there are no locations" in soup_page.find("div",attrs={"id":"rio-listWrapper"}).text:
                driver.find_element_by_xpath('//*[@id="spid17553"]').click()
                time.sleep(2)
            else:
                soup_page = BeautifulSoup(driver.page_source)
            
                records = soup_page.find_all("div",attrs={"id":"rio-listWrapper"})
                for r in range(len(records)):
                    location_name = records[r].find("strong").text + ", " + records[0].find_all("strong")[1].text
                    street_address = records[r].find("div",attrs={"class":"rio-list-addr"}).text 
                    add = records[r].find("div",attrs={"class":"rio-list-csz"}).text
                    try:
                        city,[state,zipcode] = add.split(",")[0],add.split(",")[1].strip().split(" ")
                    except:
                        city,[state,zipcode] = add,[add,add]
                    country_code = "USA"
                    location_type = soup_page.find("label",attrs={"for":"spid17601"}).text.split("[")[0].strip()
                    phone = '<MISSING>'
                    
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
                    
                driver.find_element_by_xpath('//*[@id="spid17553"]').click()
                time.sleep(2)
            
            
            
            
            driver.find_element_by_xpath('//*[@id="spid17555"]').click()
            time.sleep(2)
            soup_page = BeautifulSoup(driver.page_source)
            if "We're sorry there are no locations" in soup_page.find("div",attrs={"id":"rio-listWrapper"}).text:
                driver.find_element_by_xpath('//*[@id="spid17555"]').click()
                time.sleep(2)
            else:
                soup_page = BeautifulSoup(driver.page_source)
            
                records = soup_page.find_all("div",attrs={"id":"rio-listWrapper"})
                for r in range(len(records)):
                    location_name = records[r].find("strong").text + ", " + records[0].find_all("strong")[1].text
                    street_address = records[r].find("div",attrs={"class":"rio-list-addr"}).text 
                    add = records[r].find("div",attrs={"class":"rio-list-csz"}).text
                    try:
                        city,[state,zipcode] = add.split(",")[0],add.split(",")[1].strip().split(" ")
                    except:
                        city,[state,zipcode] = add,[add,add]
                    country_code = "USA"
                    location_type = soup_page.find("label",attrs={"for":"spid17601"}).text.split("[")[0].strip()
                    phone = '<MISSING>'
                    
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
                    
                driver.find_element_by_xpath('//*[@id="spid17555"]').click()
                time.sleep(2)
             
            
            
            driver.find_element_by_xpath('//*[@id="spid17601"]').click()
            time.sleep(2)
            soup_page = BeautifulSoup(driver.page_source)
            if "We're sorry there are no locations" in soup_page.find("div",attrs={"id":"rio-listWrapper"}).text:
                driver.find_element_by_xpath('//*[@id="spid17601"]').click()
                time.sleep(2)
            else:
                soup_page = BeautifulSoup(driver.page_source)
            
                records = soup_page.find_all("div",attrs={"id":"rio-listWrapper"})
                for r in range(len(records)):
                    location_name = records[r].find("strong").text + ", " + records[0].find_all("strong")[1].text
                    street_address = records[r].find("div",attrs={"class":"rio-list-addr"}).text 
                    add = records[r].find("div",attrs={"class":"rio-list-csz"}).text
                    try:
                        city,[state,zipcode] = add.split(",")[0],add.split(",")[1].strip().split(" ")
                    except:
                        city,[state,zipcode] = add,[add,add]
                    country_code = "USA"
                    location_type = soup_page.find("label",attrs={"for":"spid17601"}).text.split("[")[0].strip()
                    phone = '<MISSING>'
                    
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
    
                driver.find_element_by_xpath('//*[@id="spid17601"]').click()
                time.sleep(2)
        except:
            print(s)
            
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
    print(data)
    df_data.to_csv('./data.csv',index = 0,header=True,columns=['locator_domain','location_name','street_address','city',
                                                               'state','zip','country_code','store_number','phone','location_type',
                                                               'latitude','longitude','hours_of_operation','page_url'])

def scrape():
    data = fetch_data()
    write_output(data)


scrape()

    
    
    
    
    
    
    
