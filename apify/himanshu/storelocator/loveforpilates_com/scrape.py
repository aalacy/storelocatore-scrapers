import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # print("data::" + str(data))
        for i in data or []:
            writer.writerow(i)


def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    store_detail = []
    
    lat = []
    lng=[]
    return_main_object = []
    address1 = []
    base_url ='https://loveforpilates.com'
     
    

    
    r = requests.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    main =  soup.find('div', {'id': 'builder-row-58d4e40454852'}).find_all('div', {'class': 'module rich-text'})
    for i in main:
        add =(list(i.stripped_strings))
        address_tmp=add[3].split(',')
        location_name =add[1]
        phone = add[5]
       
        if(len(address_tmp)==5):
            address =address_tmp[0]+' '+address_tmp[1]
            city = address_tmp[2]
            state = address_tmp[3]
        elif(len(address_tmp)==4):
            address =address_tmp[0]
            city = address_tmp[1]
            state = address_tmp[2]
            
 
        hour =" ".join(add[-15:]).replace('|','').replace('Hours','').strip()
      
        tem_var =[]
    
        tem_var.append(base_url)
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append('<MISSING>')
        tem_var.append('US')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hour)
        tem_var.append(base_url) 
       

        return_main_object.append(tem_var)
        
           
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
