#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 20 10:54:36 2019

@author: srek
"""
import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
import time
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ppgpaints_com')



def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)

def fetch_fields(driver,location_type,country_code):
    url = "https://www.ppgpaints.com/store-locator"
    data_out = []
    soup = BeautifulSoup(driver.page_source)
    store_list = soup.find("div",attrs={"class":"store-list"}).find_all("div",attrs={"class":"store-details"})
    
    for sl in range(len(store_list)):
        #logger.info(sl)
        location_name = BeautifulSoup(str(store_list[sl].find("h2")).split('<span class="store-distance">')[0]).text
        address = store_list[sl].find("div",attrs={"class":"store-address"}).find_all("p")
        
        street_address = address[0].text.strip()
        try:
            address[1] = address[1].replace(",,",",")
        except:
            address[1] = address[1]
        #logger.info(address[1])
        if country_code == "US":
            try:
                city,[state,zipcode] = address[1].text.strip().split(",")[0],address[1].text.strip().split(",")[-1].split(" ")[1:]
            except:
                city,state = address[1].text.strip().split(",")
                zipcode = "<MISSING>"
        elif country_code == "CA":
           city = address[1].text.strip().split(",")[0]
           state = address[1].text.strip().split(",")[1].strip().split(" ")[0]
           zipcode = ' '.join(address[1].text.strip().split(",")[1].strip().split(" ")[1:])
        
        city = city.strip()
        state = state.strip()
        zipcode = zipcode.strip()
        #logger.info(store_list[sl].text)
        try:
            phone = store_list[sl].find("a",attrs={"class":"mobile-hide"}).text.replace("Call","").strip()
        except:
            #logger.info(store_list[sl])
            phone = "<MISSING>"
            
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_open = "<MISSING>"
        
        
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
    return data_out


def check_zip(x):
    #logger.info(x)
    if len(x) == 4:
        
        y = "0"+str(x)
        #logger.info(y)
    elif len(x) == 9 and str(x) !="<MISSING>":
        y = x[:5]
        logger.info(y)
    elif len(x) == 8 and str(x) !="<MISSING>":
        y = "0"+x[:4]
        logger.info(y)
    else:
        y = x
    
    return y



def phone_check(x):
    if x != "<MISSING>":
        #logger.info(x)
        y = x.replace("-","").replace(".","").strip()
        if len(y) < 10:
            logger.info(x)
            y = "<MISSING>"
        else:
            y = x
    else:
        y = x
    return y



def fetch_data():
    
    
    #df_us_list = pd.read_csv("/home/srek/xyz/Odetta/US_states.csv")
    #driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")
   
    driver = get_driver()
    data = []
    url = "https://www.ppgpaints.com/store-locator"
    
    #states_list =  pd.read_csv("/home/srek/xyz/Odetta/US_states.csv").State_modified.drop_duplicates().tolist()
    states_dict = {"US":["Alabama, USA","Alaska, USA","Arizona, USA","Arkansas, USA","California, USA","Colorado, USA","Conneticut, USA","Deleware, USA","District of Columbia, USA","Florida, USA","Georgia, USA","Hawaii, USA","Idaho, USA","Illinois, USA","Indiana, USA","Iowa, USA","Kansas, USA","Kentucky, USA","Lousiana, USA","Maine, USA","Maryland, USA","Massachusetts, USA","Michigan, USA","Minnesota, USA","Mississippo, USA","Missouri, USA","Montana, USA","Nebraska, USA","Nevada, USA","New Hampshire, USA","New Jersey, USA","New Mexico, USA","New York, USA","North Carolina, USA","North Dakota, USA","Ohio, USA","Oklahoma, USA","Oregon, USA","Pennsylvania, USA","Rhode Island, USA","South Carolina, USA","South Dakota, USA","Tennessee, USA","Texas, USA","Utah, USA","Vermont, USA","Virginia, USA","Washington, USA","West Virginia, USA","Wisconsin, USA","Wyoming, USA"],"CA":["Alberta, CA","British Columbia, CA","Manitoba, CA","New Brunswick, CA","Newfoundland and Labrador, CA","Northwest Territories, CA","Nova Scotia, CA","Nunavut, CA","Ontario, CA","Prince Edward Island, CA","Quebec, CA","Saskatchewan, CA","Yukon, CA"]}
    #states_list = ["Alberta, CA","British Columbia, CA","Manitoba, CA","New Brunswick, CA","Newfoundland and Labrador, CA","Northwest Territories, CA","Nova Scotia, CA","Nunavut, CA","Ontario, CA","Prince Edward Island, CA","Quebec, CA","Saskatchewan, CA","Yukon, CA"]
    #country_code = "US"
    driver.get(url)
    time.sleep(3)
    countries = list(states_dict.keys())
    
    for c in range(len(countries)):
        states_list = states_dict[countries[c]]
        country_code = countries[c]
        
        for st in range(len(states_list)):
            logger.info(st)
            element = driver.find_element_by_id("userAddress")
            element.clear()
            element.send_keys(states_list[st])
            
            driver.find_element_by_id("submit-find-location").click()
            time.sleep(3)
            
            #swiper-slide ppgpaints-filter
            location_type = "PGG Paints"
            driver.find_element_by_xpath("/html/body/main/div/div/section/form/div[2]/div/div/div[2]/div[2]/div/button[1]").click()
            time.sleep(1)
            data = data + fetch_fields(driver,location_type,country_code)
            driver.find_element_by_xpath("/html/body/main/div/div/section/form/div[2]/div/div/div[2]/div[2]/div/button[1]").click()
            time.sleep(1)
            
            location_type = "Home Depot"
            driver.find_element_by_xpath("/html/body/main/div/div/section/form/div[2]/div/div/div[2]/div[2]/div/button[2]").click()
            time.sleep(1)
            data = data+fetch_fields(driver,location_type,country_code)
            driver.find_element_by_xpath("/html/body/main/div/div/section/form/div[2]/div/div/div[2]/div[2]/div/button[2]").click()
            time.sleep(1)
        
            location_type = "Independent Retailers"
            driver.find_element_by_xpath("/html/body/main/div/div/section/form/div[2]/div/div/div[2]/div[2]/div/button[3]").click()
            time.sleep(1)
            data = data + fetch_fields(driver,location_type,country_code)
            driver.find_element_by_xpath("/html/body/main/div/div/section/form/div[2]/div/div/div[2]/div[2]/div/button[3]").click()
            time.sleep(1)
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


