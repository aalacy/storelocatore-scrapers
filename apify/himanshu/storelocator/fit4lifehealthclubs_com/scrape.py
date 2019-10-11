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
    store_name = []
    return_main_object = []
    address1 = []
    phone = ''
    
    r = requests.get(
    "https://fit4lifehealthclubs.com/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    k  = soup.find('li', {'id': 'menu-item-864'}).find_all('ul',{'class':'sub-menu'})
    for i in k:

        link1 = i.find_all('a')
        

        for i in link1: 
                link = i['href']
                location_name= i.text
                 
                
                r1 = requests.get(link, headers=headers)
                soup1 = BeautifulSoup(r1.text, "lxml")
                address_tmp = soup1.find_all('div',{'class':'wpb_text_column'})
                lng = soup1.find_all('iframe')[1]['src'].split('!2d')[1].split('!3d')[0]             
                lat = soup1.find_all('iframe')[1]['src'].split('!2d')[1].split('!3d')[1].split('!')[0]
               
              
                tem_var =[]
                if(len(address_tmp) ==11):
                        address_tmp1= address_tmp[3]
                        address_tmp2=list(address_tmp1.stripped_strings)                       
                        hour = address_tmp[-1].text.strip().replace('\n','').strip().replace('\xa0','').strip().replace('        ','')
                        if(len(address_tmp2)==2):
                                address_tmp3= address_tmp[2]
                                address_tmp4=list(address_tmp3.stripped_strings)
                                address = address_tmp4[1]
                                city_tmp = address_tmp4[2].split(',')
                                city =city_tmp[0]
                                state_tmp = city_tmp[1].split(' ')
                                state = state_tmp[1]
                                zip1 =state_tmp[2]
                                phone_tmp = address_tmp[3]
                                phone_tmp1= list(phone_tmp.stripped_strings)
                                phone = phone_tmp1[1]
                                
                                
                        elif(len(address_tmp2)==5):
                                address_tmp3= address_tmp[3]
                                address_tmp4=list(address_tmp3.stripped_strings)
                                address = address_tmp4[1].replace('(Brinkley Commons – Next to new Walmart)','')
                                city_tmp = address_tmp4[2].split(' ')
                                phone_tmp = address_tmp[3]
                                phone_tmp1= list(phone_tmp.stripped_strings)
                                phone = phone_tmp1[4]
                                
                                
                                if(len(city_tmp)==3):
                                        city =city_tmp[0]
                                        state = city_tmp[1].replace('\u200e','')
                                        
                                        zip1 = city_tmp[2].replace('\u200e','')
                                        
                                elif(len(city_tmp)==4):
                                        city =city_tmp[0]+''+city_tmp[1]
                                        state =city_tmp[2]
                                        zip1= city_tmp[3]
                                        

                        elif(len(address_tmp2)==6):
                                address_tmp3= address_tmp[3]
                                address_tmp4=list(address_tmp3.stripped_strings)  
                                address = address_tmp4[2]
                                city_tmp =address_tmp4[3].split(',')
                                city =city_tmp[0]
                                state_tmp = city_tmp[1].split(' ')
                                state =state_tmp[1]
                                zip1 =state_tmp[2]
                               
                elif(len(address_tmp) ==10):
                        address_tmp3= address_tmp[2]
                        address_tmp4=list(address_tmp3.stripped_strings)
                        hour = address_tmp[-1].text.strip().replace('\n','').strip().replace('\xa0','').strip().replace('        ','')
                        
                      
                        if(len(address_tmp4)==6):
                                address = address_tmp4[2]
                                city_tmp = address_tmp4[3].split(',')
                                city =city_tmp[0]
                                state_tmp = city_tmp[1].split(' ')
                                state = state_tmp[1]
                                zip1= state_tmp[2].replace('xa','').strip()
                                phone = address_tmp4[5]
                                
                               
                               
                        if(len(address_tmp4)==5):
                                address =address_tmp4[1]
                                city_tmp = address_tmp4[2].split(',')
                                city =city_tmp[0]
                                state_tmp = city_tmp[1].split(' ')
                                state =state_tmp[1]
                                zip1= state_tmp[2]
                                phone = address_tmp4[4]
                              
                                
                        if(len(address_tmp4)==8):
                                address =address_tmp4[2]
                                city_tmp = address_tmp4[3].split(',')
                                city = city_tmp[0]
                                state_tmp = city_tmp[1].split(' ')
                                state =state_tmp[1]
                                zip1= state_tmp[2]
                                phone = address_tmp4[5]
                                
                          
                elif(len(address_tmp) ==3):  
                        address_tmp3= address_tmp[1]
                        address_tmp4=list(address_tmp3.stripped_strings) 
                        address = address_tmp4[1]
                        city_tmp =address_tmp4[2].split(',')
                        city =city_tmp[0]
                        state_tmp = city_tmp[1].split(' ')
                        state = state_tmp[1]
                        zip1= state_tmp[2] 
                        phone = '<MISSING>'
                        hour =  '<MISSING>'
                      
                        
                elif(len(address_tmp) ==9):
                        address_tmp3= address_tmp[2]
                        address_tmp4=list(address_tmp3.stripped_strings) 
                        address =address_tmp4[2]
                        city_tmp = address_tmp4[3].split(',')
                        city =city_tmp[0]
                        state_tmp = city_tmp[1].split(' ')
                        state = state_tmp[1]
                        zip1 = state_tmp[2]
                        phone = address_tmp4[5]
                        hour = address_tmp[-1].text.strip().replace('\n','').strip().replace('\xa0','').strip().replace('        ','')
                      
                         

                elif(len(address_tmp) ==12):
                        address_tmp3= address_tmp[3]
                        address_tmp4=list(address_tmp3.stripped_strings)   
                        address = address_tmp4[2]
                        city_tmp = address_tmp4[3].split(',')
                        city =city_tmp[0]
                        state_tmp = city_tmp[1].split(' ')
                        state = state_tmp[1].replace('xa','')
                        zip1 = state_tmp[2]
                        phone_tmp = address_tmp[4]
                        phone_tmp1= list(phone_tmp.stripped_strings) 
                        phone = phone_tmp1[1]
                        hour = address_tmp[-1].text.strip().replace('\n','').strip().replace('\xa0','').strip().replace('        ','')
                        
                tem_var.append('https://fit4lifehealthclubs.com/')
                tem_var.append(location_name)
                tem_var.append(address)
                tem_var.append(city)
                tem_var.append(state) 
                tem_var.append(zip1)
                tem_var.append('US')
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("<MISSING>")
                tem_var.append(lat)
                tem_var.append(lng)
                tem_var.append(hour)
                tem_var.append(link) 
                print(tem_var)              
                return_main_object.append(tem_var) 
              
               



       
         
                   
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
