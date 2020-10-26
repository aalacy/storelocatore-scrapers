#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep 15 12:12:22 2019

@author: srek
"""
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time
from selenium.webdriver.chrome.options import Options
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('chuckecheese_com')



def get_driver():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', options=options)

def fetch_data():
    url = "https://www.chuckecheese.com/locations"
    data = []
    
    locator_domain = url
    
    driver = get_driver()
    driver.get(url)
    
    
    state_list = ['Huntsville, AL', 'Anchorage, AK', 'Phoenix, AZ', 'Little Rock, AR', 'Sacramento, CA', 'Los Angeles, CA', 'Beverly Hills, CA', 'Denver, CO', 'Hartford, CT', 'Dover, DE', 'Washington, DC', 'Pensacola, FL', 'Miami, FL', 'Orlando, FL', 'Atlanta, GA', 'Honolulu, HI', 'Montpelier, ID', 'Chicago, IL', 'Springfield, IL', 'Indianapolis, IN', 'Davenport, IA', 'Des Moines, IA', 'Wichita, KS', 'Hazard, KY', 'New Orleans, LA', 'Freeport, ME', 'Baltimore, MD', 'Boston, MA', 'Coldwater, MI', 'Gaylord, MI', 'Duluth, MN', 'Biloxi, MS', 'St. Louis, MO', 'Laurel, MT', 'Hastings, NE', 'Reno, NV', 'Ashland, NH', 'Livingston, NJ', 'Santa Fe, NM', 'New York, NY', 'Oxford, NC', 'Walhalla, ND', 'Cleveland, OH', 'Tulsa, OK', 'Portland, OR', 'Pittsburgh, PA', 'Newport, RI', 'Camden, SC', 'Aberdeen, SD', 'Nashville, TN', 'Austin, TX', 'Logan, UT', 'Killington, VT', 'Altavista, VA', 'Bellevue, WA', 'Beaver, WV', 'Milwaukee, WI', 'Pinedale, WY']
       
    
    for sl in range(len(state_list)):
        lookup_keyword = state_list[sl]
        
        element = driver.find_element_by_id("locationInput")
        element.clear()
        element.send_keys(lookup_keyword)
        
        driver.find_element_by_id("locationSubmit").click()
        time.sleep(8)
        soup = BeautifulSoup(driver.page_source,"html.parser")
        records = soup.find_all("li",attrs={"class":"location__card col-sm-6 col-md-6 col-lg-4 show"})
        
        
        for r in range(len(records)):
            data_record = {}
            
            location_name = records[r].find("header").text.replace("\n","")
            state = location_name.split(",")[-1].strip()
            
            city = location_name.replace(state,"").replace(",","").strip()
            
            address = list(filter(None, records[r].find("address").text.strip().split("\n")))
            if len(address) == 2:
                street_address = address[0]
                zipcode = address[1].replace(records[r].find("header").text.replace("\n",""),"").strip()
            
            hours_of_open = records[r].find("span",attrs={"class":"store-hours"}).text
            phone = records[r].find("a",attrs={"class":"location__tel notShown"}).text
            latitude,longitude = records[r].find("a",attrs={"class":"arrow notShown"}).get("href").split("destination=")[1].split(",")
            
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
            logger.info(len(data))
            
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
        
        
        
        
        
