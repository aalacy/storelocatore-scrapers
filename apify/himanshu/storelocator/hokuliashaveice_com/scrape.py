import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', 'w') as output_file:
        writer = csv.writer(output_file, delimiter=",")

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])

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
    base_url ='https://hokuliashaveice.com/locations/'
    domain_url = 'https://hokuliashaveice.com/'
    

    r = requests.get(base_url, headers=headers)
    
    soup = BeautifulSoup(r.text, "lxml")    
    main =soup.find_all('div', {'class': 'col-xs-6'})

    for i in main:
        address1 =" ".join(list(i.stripped_strings))
        if "Coming soon" in address1:
            continue
        address2 =list(i.stripped_strings)
        if(len(address2)==4):
            location_name = address2[0]
            address = address2[1]
            city_tmp = address2[2].split(',')
            if(len(city_tmp)==2):
                city= city_tmp[0]
                state_tmp= city_tmp[1].split(' ')
                if(len(state_tmp)==2):
                    state= state_tmp[1].replace('Alaska','AL')
                    zip = '<MISSING>'
                elif(len(state_tmp)==3):
                    state_tmp= city_tmp[1].strip().split()
                    state = state_tmp[0].replace('Texas','TX').replace('Utah','UT').replace('.','')
                    zip = state_tmp[1]
                elif(len(state_tmp)==4):
                    state = state_tmp[1]
                    zip = state_tmp[3]    
                    
            elif(len(city_tmp)==1):
                city= address2[1].split(',')[0]
                state= address2[1].split(',')[1].strip()
                zip = '<MISSING>'
        elif(len(address2)==5):
            location_name = address2[0]
            address1 = address2[1]
            if(address1.isnumeric()):
                address =address2[1]
                print(address)
                
        # if(len(address2))
        # 

        # address = address2[1]

        # print(address)

    # for i in main:
    #     lat.append(i.attrs['data-lat'])
    #     lng.append(i.attrs['data-lng'])
    
    # for index,i in enumerate(r,start=0):
    #     tem_var =[]
    #     obj= r[i]
    #     location_name = obj['name']
    #     address =obj['street']
    #     city_tmp = obj['address'].split(',')
    #     city =city_tmp[0]
    #     state_tmp = city_tmp[1].split(' ')
    #     state= state_tmp[1]
    #     phone= obj['phone'].replace('JOES','')
    #     zip =state_tmp[2]
    #     hour1=BeautifulSoup( obj['hours'], "lxml" )
    #     hour =" ".join(list(hour1.stripped_strings)).replace('Online Ordering is not yet available at this location. Please call to place your order. Thank you!','')
        
    #     tem_var.append(domain_url)
    #     tem_var.append(location_name)
    #     tem_var.append(address)
    #     tem_var.append(city)
    #     tem_var.append(state) 
    #     tem_var.append(zip)
    #     tem_var.append('US')
    #     tem_var.append("<MISSING>")
    #     tem_var.append(phone)
    #     tem_var.append("<MISSING>")
    #     tem_var.append(lat[index])
    #     tem_var.append(lng[index])
    #     tem_var.append(hour)
    #     tem_var.append('https://www.orderjoes.com/locations/') 
    #     print(tem_var)

    # return_main_object.append(tem_var)
        
           
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
