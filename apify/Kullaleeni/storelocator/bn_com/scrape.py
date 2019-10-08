#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 14 10:03:54 2019

@author: srek
"""



import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

def fetch_data():
    #state_list = pd.read_csv("/home/srek/xyz/Odetta/US_states.csv").State_modified.dropna().tolist()
    state_list = ['Huntsville, AL', 'Anchorage, AK', 'Phoenix, AZ', 'Little Rock, AR', 'Sacramento, CA', 'Los Angeles, CA', 'Beverly Hills, CA', 'Denver, CO', 'Hartford, CT', 'Dover, DE', 'Washington, DC', 'Pensacola, FL', 'Miami, FL', 'Orlando, FL', 'Atlanta, GA', 'Honolulu, HI', 'Montpelier, ID', 'Chicago, IL', 'Springfield, IL', 'Indianapolis, IN', 'Davenport, IA', 'Des Moines, IA', 'Wichita, KS', 'Hazard, KY', 'New Orleans, LA', 'Freeport, ME', 'Baltimore, MD', 'Boston, MA', 'Coldwater, MI', 'Gaylord, MI', 'Duluth, MN', 'Biloxi, MS', 'St. Louis, MO', 'Laurel, MT', 'Hastings, NE', 'Reno, NV', 'Ashland, NH', 'Livingston, NJ', 'Santa Fe, NM', 'New York, NY', 'Oxford, NC', 'Walhalla, ND', 'Cleveland, OH', 'Tulsa, OK', 'Portland, OR', 'Pittsburgh, PA', 'Newport, RI', 'Camden, SC', 'Aberdeen, SD', 'Nashville, TN', 'Austin, TX', 'Logan, UT', 'Killington, VT', 'Altavista, VA', 'Bellevue, WA', 'Beaver, WV', 'Milwaukee, WI', 'Pinedale, WY']
    data = []
    for s in range(len(state_list)):
        state = state_list[s]
        
        pagenumber = 0
        url = "https://stores.barnesandnoble.com/stores?page={}&size=100&searchText={}&view=list&storeFilter=all".format(pagenumber,state.replace(", ","%2C+"))
        
        page = requests.get(url)
        
        soup = BeautifulSoup(page.text,"html.parser")
        
        if "Did you mean?" in soup.find("div",attrs={"class":"col-sm-8 col-md-8 col-lg-8 col-xs-8"}).text:
            options = soup.find("div",attrs={"class":"col-sm-8 col-md-8 col-lg-8 col-xs-8"}).find_all("a")
            options = ['https://stores.barnesandnoble.com'+o.get("href").replace("/stores?","/stores?page=0&size=100&") for o in options]
    
            for op in range(len(options)):
                page = requests.get(options[op])
                soup = BeautifulSoup(page.text,"html.parser")
                
        if "No results found" not in soup.find("h3").text:
        
            noofresults = soup.find("h3",attrs={"class":"lgTitlesBlack"}).text.split("\n")
            
            noofresults = ' '.join([nr.strip() for nr in noofresults]).strip()
            
            noofresults = int(noofresults.split("stores  within 50 miles of")[0].split("of")[-1].strip())
            
            
            if noofresults > 100:
                print(noofresults)
                        
            records = soup.find_all("div",attrs={"class":"col-sm-12 col-md-8 col-lg-8 col-xs-12"})
            
            for r in range(len(records)):
                record = records[r]
                link = "https://stores.barnesandnoble.com"
                
                locator_domain = url
                location_link = link + record.find("a").get("href")
                
                location_page = requests.get(location_link)
                
                location_soup = BeautifulSoup(location_page.text,"html.parser")
                
                location_name = location_soup.find("h3").text.split("\n")
                
                location_name = ' '.join(list(filter(None, [l.strip() for l in location_name])))
                
                address_block = location_soup.find("div",attrs={"class":"col-sm-8 col-md-4 col-lg-4 col-xs-6"}).text.split("\n")
                
                
                address_block = list(filter(None, [ab.strip() for ab in address_block]))
                
                phone =  []
                remove_from_address = []
                for ad in range(len(address_block)):
                    try:
                        phone.append(re.compile(r'\d\d\d-\d\d\d-\d\d\d\d').search(address_block[ad]).group(0))
                        remove_from_address.append(address_block[ad])
                    except:
                        pass
                    if 'Connect with us:' in address_block[ad]:
                        remove_from_address.append(address_block[ad])
                              
                [address_block.remove(p) for p in remove_from_address]
                
                hours_of_open = address_block[address_block.index("Store Hours:"):]
                
                [address_block.remove(p) for p in hours_of_open]
                hours_of_open = ', '.join(hours_of_open)
                
                city,state_zip = address_block[-1].split(",")
                
                state,zipcode = state_zip.strip().split(" ")
                
                street_address = ', '.join(address_block[:-1])
                
                country_code = "US"
                store_number = "<MISSING>"
                location_type = "<MISSING>"
                latitude = "<MISSING>"
                longtitude = "<MISSING>"
                
                 
                data_record = {}
                #print(address)
                data_record['locator_domain'] = locator_domain
                data_record['location_name'] = location_name
                data_record['street_address'] = street_address
                data_record['city'] = city
                data_record['state'] = state
                data_record['zip'] = zipcode
                data_record['country_code'] = country_code
                data_record['store_number'] = store_number
                data_record['phone'] = phone[0]
                data_record['location_type'] = location_type
                data_record['latitude'] = latitude
                data_record['longitude'] = longtitude
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
























































