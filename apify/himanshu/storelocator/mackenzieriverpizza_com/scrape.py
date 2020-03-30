# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json




session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)




def fetch_data():
    base_url = "https://www.mackenzieriverpizza.com/locations/"
    r = session.get(base_url)
    main_soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    store_names=[]
    k = main_soup.find_all('div',{'class':"et_builder_inner_content et_pb_gutters3"})
    
    latitude = []
    longitude = []
    store_detail =[]
    hours=[]
    for i in k:
        times = i.find_all('div',{"class","et_pb_text_inner"})
        for time in times:
            if time.find('p',{"class":"big"}).a:
                if len(time.find('p',{"class":"big"}).a['href'].split('@')) ==2:
                    lat_lgt = time.find('p',{"class":"big"}).a['href'].split('@')[1].split('z/')[0].split(',')[0:2]
                    latitude1 = lat_lgt[0]
                    longitude1 = lat_lgt[1]
                else:
                    latitude1 = '<MISSING>'
                    longitude1 = '<MISSING>' 
                latitude.append(latitude1)    
                longitude.append(longitude1)

            else:
                latitude.append('<MISSING>')    
                longitude.append('<MISSING>') 
          
            t = ''
            data=(list(time.p.stripped_strings)[2::])
            for j in data:
                t= t+ ' ' +j
            hours.append(t.replace('702-916-2999',''))
   
 
   ####------------------inside of data-----------
    for i in k:
        link = i.find_all('h3')
        for index,j in enumerate(link):
            if j.a != None:
                store_names.append(j.a.text)
                temp=[]
                temp_var=[]
                r = session.get(j.a['href'])
                soup = BeautifulSoup(r.text,"lxml")
                if (soup.find('div',{"class":"et_pb_text_inner"}).find('p')):
                    temp = list(soup.find('div',{"class":"et_pb_text_inner"}).find('p').stripped_strings)
                else:
                    temp = list(soup.find('div',{"class":"et_pb_row et_pb_row_1"}).find('p').stripped_strings)

                if "3411 Princeton Road" in temp  or "1205 Eglin St." in temp:
                    temp =temp[-1:]  +temp[:1]+ temp[1:2]
                
                state_zip=temp[2].split(',')[1].split( )
                street_address=temp[1]
                city = temp[2].split(',')[0]
                state = state_zip[0]
                if len(state_zip)==1:
                    zipcode="<MISSING>"
                else:
                    zipcode = state_zip[1]
                phone=temp[0]

                temp_var.append(street_address)
                temp_var.append(city)
                temp_var.append(state)
                temp_var.append(zipcode)
                temp_var.append("US")
                temp_var.append("<MISSING>")
                temp_var.append(phone)
                temp_var.append("<MISSING>")
                store_detail.append(temp_var)
    
    for i in range(len(store_names)):
        store=list()
        store.append("https://www.mackenzieriverpizza.com")
        store.append(store_names[i])
        store.extend(store_detail[i])
        store.append(latitude[i])
        store.append(longitude[i])
        store.append(hours[i])
        return_main_object.append(store)

    return return_main_object



def scrape():
    data = fetch_data()
    write_output(data)


scrape()