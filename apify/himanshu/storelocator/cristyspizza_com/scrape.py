import csv
import requests
from bs4 import BeautifulSoup
import re
# import http.client
import json
# import  pprint
import time

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
 
def fetch_data():
    base_url = "https://cristyspizza.com"
    get_url='https://cristyspizza.com/locations/' 

    return_main_object = []
    
    # search.current_zip """"""""==zip
    header = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36',
              "Content-Type":"application/x-www-form-urlencoded",
               "Referer": "https://bylinebank.locatorsearch.com/index.aspx?s=FCS"
              }
     
       
     
    r= requests.get(get_url,headers=header)
    soup = BeautifulSoup(r.text,"lxml")
    main = soup.find_all("div",{'class':"fl-html"})
   
    for i in main:                  
            main1 = list(i.stripped_strings)            
            if main1 !=[]:
                main2 = list(i.stripped_strings)
                location_name = main2[0]
                address= main2[1]
                city_tmp = main2[2].split(',')
                city = city_tmp[0]
                state_tmp = city_tmp[1].strip().split(' ')
                state = state_tmp[0]
                zip = state_tmp[1]
                phone = main2[3]
                country_code = 'US'
            
                hour1 = "".join(main2).replace(location_name,'').replace(location_name,'').replace(address,'').replace(city,'').replace(state,'').replace(zip,'').replace(phone,'').strip()
                hour2 = hour1.replace('Carryout, Delivery','').replace(', Dine-in','').replace(',Drive Thru','').replace(', Dine-In','').replace(', Drive Thru','')
                hour = hour2.replace(',  Open from April to October:','').replace('Dine-in, Carryout','').replace('Hours:','').replace(',  Carryout/Delivery:','').replace(',  ','')
                # print(city)
                # print('==============')
            link1 = i.find('a')
            if link1!=None:
                link1 = i.find('a')['href']
                link2 = base_url+link1
                link = link2.replace('https://cristyspizza.comhttp://www.papaboos.com','http://www.papaboos.com')               
                r1= requests.get(link,headers=header)
                soup1 = BeautifulSoup(r1.text,"lxml")            
                lat_tmp= soup1.find_all('iframe')[1]['src'].split('!2d')
                lng = lat_tmp[1].split('!3d')[0]
                lat = lat_tmp[1].split('!3d')[1].split('!2m3')[0]
                
                
                store = []
                store.append(base_url if base_url else '<MISSING>')
                store.append(location_name if location_name else '<MISSING>')
                store.append(address if address else '<MISSING>')
                store.append(city if city else '<MISSING>')
                store.append(state if state else '<MISSING>')
                store.append(zip if zip else '<MISSING>')
                store.append(country_code if country_code else '<MISSING>')
                store.append('<MISSING>')
                store.append(phone if phone else '<MISSING>')
                store.append('<MISSING>')
                store.append(lat if lat else '<MISSING>')
                store.append(lng if lng else '<MISSING>')
                store.append(hour if hour else '<MISSING>')
                store.append(link)
                print(store)
                return_main_object.append(store)
            # if store[2] in addresses:
            #     continue
            # addresses.append(store[2])

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            # yield store
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
