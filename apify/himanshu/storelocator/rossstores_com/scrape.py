#!/usr/bin/env python
# coding: utf-8

# In[1]:


import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip



def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def minute_to_hours(time):
    am = "AM"
    hour = int(time / 60)
    if hour > 12:
        am = "PM"
        hour = hour - 12
    if int(str(time / 60).split(".")[1]) == 0:
        return str(hour) + ":00" + " " + am
    else:
        return str(hour) + ":" + str(int(str(time / 60).split(".")[1]) * 6) + " " + am


def fetch_data():
    zips = sgzip.for_radius(100)
    
    return_main_object = []
    addresses = []
    store_name=[]
    store_detail=[]
  

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
        "Accept": "/",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    }

    # it will used in store data.
    locator_domain = "https://www.drmartens.com"
    location_name = ""
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zipp = "<MISSING>"
    country_code = "US"
    store_number = "<MISSING>"
    phone = "<MISSING>"
    location_type = "drmartens"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    raw_address = ""
    hours_of_operation = "<MISSING>"
    address=[]
    for zip_code in zips:
        # print("zips === " + str(zip_code))
        r = requests.get(
            'https://hosted.where2getit.com/rossdressforless/2014/ajax?xml_request=<request><appkey>097D3C64-7006-11E8-9405-6974C403F339</appkey><formdata id="locatorsearch"><dataview>store_default</dataview><limit>1000</limit><geolocs><geoloc><addressline>'+str(zip_code)+'</addressline><country>US</country></geoloc></geolocs><searchradius>100</searchradius></formdata></request>',
            headers=headers)
        
        soup= BeautifulSoup(r.text,"lxml")
        
        monday=soup.find_all("monday")
        tuesday=soup.find_all("tuesday")
        wednesday=soup.find_all("wednesday")
        thursday=soup.find_all("thursday")
        friday = soup.find_all("friday")
        saturday=soup.find_all("saturday")
        sunday=soup.find_all("sunday")
        # print(soup.find_all("friday"))
        st1 = soup.find_all("address1")
        city1 = soup.find_all("city")
        state1 = soup.find_all("state")
        name1 = soup.find_all("name")
        phone1 = soup.find_all("phone")
        postalcode1= soup.find_all("postalcode")
        latitude1 = soup.find_all("latitude")
        longitude1 = soup.find_all("longitude")

    
        for index,i in enumerate(st1):
            tem_var=[]
            hours = (monday[index].text + ' ' + tuesday[index].text + ' '+wednesday[index].text + ' '+ thursday[index].text + ' ' +friday[index].text + ' '+ saturday[index].text+ ' '+sunday[index].text)

            tem_var.append("https://www.rossstores.com")
            tem_var.append(name1[index].text)
            tem_var.append(st1[index].text)
            tem_var.append(city1[index].text)
            tem_var.append(state1[index].text)
            tem_var.append(postalcode1[index].text)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")

            tem_var.append("rossstores")
            tem_var.append(latitude1[index].text)
            tem_var.append(longitude1[index].text)
            tem_var.append(hours)
           
            
            if tem_var[3] in address:
                continue
        
            address.append(tem_var[3])

            return_main_object.append(tem_var) 
            
        
               

           

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()





