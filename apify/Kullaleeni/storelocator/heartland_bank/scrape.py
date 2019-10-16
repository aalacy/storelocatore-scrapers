#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 28 18:27:42 2019

@author: srek
"""
import pandas as pd
from bs4 import BeautifulSoup
import requests
from lxml import html

def scrape_atm_locations():
    atm_url = "https://www.heartland.bank/LEARNING/FAQs/Entries/what-are-your-current-atm-locations"
    page_atm = requests.get(atm_url)
    #soup_atm = BeautifulSoup(page_atm.text)
    #soup_atm.find("div",attrs={"class":"EDN_article-content"}).find("ul")
    location_time=[]

    tree = html.fromstring(page_atm.content)
    atm_locations = []
    atm_add = []
    for j in range(1,20):
        atm_locations.append(tree.xpath('/html/body/form/div[3]/div[4]/main/div[2]/div[3]/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[1]/div/div/div/ul/li[{}]/text()'.format(j))[0])
        atm_add.append(tree.xpath('/html/body/form/div[3]/div[4]/main/div[2]/div[3]/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[1]/div/div/div/ul/li[{}]/a/text()'.format(j))[0])
        try:
            lt1 = tree.xpath('/html/body/form/div[3]/div[4]/main/div[2]/div[3]/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[1]/div/div/div/ul/li[{}]/ul/li[1]/text()'.format(j))[0]
            lt2 = tree.xpath('/html/body/form/div[3]/div[4]/main/div[2]/div[3]/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[1]/div/div/div/ul/li[{}]/ul/li[2]/text()'.format(j))[0]
            lt3 = tree.xpath('/html/body/form/div[3]/div[4]/main/div[2]/div[3]/div[1]/div[1]/div/div/div[1]/div/div/div/div[1]/div/div[1]/div/div/div/ul/li[{}]/ul/li[3]/text()'.format(j))[0]
            location_time.append(str(lt1)+str(lt2)+str(lt3) )
        except:
            location_time.append("")
    return atm_locations,atm_add,location_time
   
    
    
def fetch_data():
    url = "https://www.heartland.bank/Locations"
    locator_domain = url
    data = []

    soup = BeautifulSoup(requests.get(url).text)
    #links = []
    atm_locations,atm_add,location_time = scrape_atm_locations()
    
    atm_locations = [k.replace(":\xa0","") for k in atm_locations]
    atm_add = [kk.replace("\xa0","") for kk in atm_add]
    atm_index = []
    
    options = soup.find("select",attrs={"id":"selectLocation"}).find_all("option")
    for o in range(1,len(options)):
        page_url = "https://www.heartland.bank"+ options[o]["value"]
        soup_page = BeautifulSoup(requests.get(page_url).text)
        location_name = soup_page.find("div",attrs={"id":"dnn_Top2Left8"}).text.replace("\n","")
        add_ = str(soup_page.find("p",attrs={"class":"blueAddress"})).split("<br/>")
        add_ = [BeautifulSoup(p).text for p in add_]
        city_state = add_[-1]
        city,[state,zipcode]  = city_state.split(",")[0], add_[-1].split(",")[1].strip().split(" ")
        city = city.strip()
        state = state.strip()
        zipcode = zipcode.strip()
        add_.remove(city_state)
        street_address = ",".join(add_)
        for x in soup_page.find_all("p"):
            if "phone" in x.text.lower():
                phone = x.text.lower().split("\n")[0].replace("phone:","").strip()
        
        hours_of_operation = []
        tables = soup_page.find_all("p",attrs={"class":"Detail"})
        
        for t in range(len(tables)):
            hours_of_operation.append(tables[t].text + " - "+soup_page.find_all("table",attrs={"class":"locationTable table-responsive"})[t].text[3:-3].replace(".\n\n\n"," ; ").replace("\n\n\n"," - "))
        
        location_type = []
        for h in range(len(hours_of_operation)):
            location_type.append(hours_of_operation[h].split("-")[0].strip())
        
        if location_name in atm_locations:
            location_type.append("ATM")
            atm_index.append(atm_locations.index(location_name))
            
        #hours_of_operation = ' ; '.join(hours_of_operation)            
        country_code = "US"
        #location_type = '<MISSING>'
        
        lat_lon = soup.find("div",attrs={"class":"edMaps_moduleWrapper"}).find("script")#.text.split("\\r\\n\\t\\r\\n")[-1]
        
        import re
        try:
            latitude = re.search("\"latitude\":\d+.\d+",str(lat_lon))[0].replace("\"latitude\":","")
        except:
            latitude = re.search("\"latitude\":-\d+.\d+",str(lat_lon))[0].replace("\"latitude\":","")


        try:
            longitude = re.search("\"longitude\":\d+.\d+",str(lat_lon))[0].replace("\"longitude\":","")
        except:
            longitude = re.search("\"longitude\":-\d+.\d+",str(lat_lon))[0].replace("\"longitude\":","")
        
        
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
        data_record['location_type'] = location_type#.strip()
        data_record['latitude'] = latitude
        data_record['longitude'] = longitude
        data_record['hours_of_operation'] = hours_of_operation
        data_record['page_url'] = page_url
        data.append(data_record)
    
    
    atm_add_del = [atm_add[al] for al in atm_index]
    
    atm_dict = {}
    for ad in range(len(atm_locations)):
        if location_time[ad] == [] :
            atm_dict[atm_add[ad]] = atm_locations[ad]
        else:
            atm_dict[atm_add[ad]] = atm_locations[ad]+";;"+str(location_time[ad])
    
    
    [atm_add.remove(aad) for aad in atm_add_del]
        
    for ad1 in atm_add:
        location_name,hours_of_operation = atm_dict[ad1].split(";;")

        data_record,city,state_zip = ad1.split(",")
        
        state,zipcode = state_zip.strip().split(" ")
            
        data_record = {}
        data_record['locator_domain'] = locator_domain.strip()
        data_record['location_name'] = location_name.strip()
        data_record['street_address'] = street_address.strip()
        data_record['city'] = city.strip()
        data_record['state'] = state.strip()
        data_record['zip'] = zipcode.strip()
        data_record['country_code'] = country_code
        data_record['store_number'] = '<MISSING>'
        data_record['phone'] = '<MISSING>'
        data_record['location_type'] = location_type#.strip()
        data_record['latitude'] = '<MISSING>'
        data_record['longitude'] = '<MISSING>'
        data_record['hours_of_operation'] = hours_of_operation
        data_record['page_url'] = "https://www.heartland.bank/LEARNING/FAQs/Entries/what-are-your-current-atm-locations"
        data.append(data_record)

    return data     
                
def write_output(data):
    df_data = pd.DataFrame(columns=['locator_domain','location_name','street_address','city','state','zip','country_code','store_number','phone','location_type','latitude','longitude','hours_of_operation'])
    
    for d in range(len(data)):
        df = pd.DataFrame(list(data[d].values())).transpose()
        df.columns = list((data[d].keys()))   
        df_data = df_data.append(df)
        #break
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

