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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    base_url= "http://mariscoselpaisa.com/cr_crew.html"
    domain_url ='http://mariscoselpaisa.com/'
  
    r = session.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    
    store_name=[]
    store_detail=[]
    
    return_main_object=[]

    k= (soup.find('div',{"id":"pagetext"})).find_all('div',{"class":"btxt_item_med"})
    # print(k)
    
    
    for i in k:
               
        add_tmp = i.find('div',{"class":"btxt_desc_med"})
        location_name = list(add_tmp.stripped_strings)[0]
        address_tmp = list(add_tmp.stripped_strings)[2]        
        if(len(add_tmp)==9):
            address_tmp = list(add_tmp.stripped_strings)[2]
            if(len(address_tmp)<100):              
                address_tmp = list(add_tmp.stripped_strings)[2].split('.')
                address = address_tmp[0]
                city_tmp = address_tmp[1].split(',')
                city = city_tmp[0]
                state =city_tmp[1]
                zip =address_tmp[2].split(' ')[1]
                phone = list(add_tmp.stripped_strings)[3].replace('su numero de telefono es ','').strip()
                lat = '<MISSING>'
                lng = '<MISSING>'
                hour = '<MISSING>'
        elif(len(add_tmp)==7):
            address_tmp = list(add_tmp.stripped_strings)[1].split('por estar en')   
            address_tmp1 = address_tmp[1].split('.')
            address =address_tmp1[0].strip()
            city_tmp = address_tmp1[1].split(',')
            city =city_tmp[0].strip()
            state = city_tmp[1].strip()
            zip =address_tmp1[2].split(' ')[1].strip()
            phone = list(add_tmp.stripped_strings)[2].strip()            
        elif(len(add_tmp)==11):
            address_tmp = list(add_tmp.stripped_strings)[2].split('.')
            address =address_tmp[0].strip()
            city_tmp= address_tmp[1].split(',')
            city =city_tmp[0].strip()
            state = city_tmp[1].strip()
            zip = address_tmp[2].strip()
            phone = list(add_tmp.stripped_strings)[3].strip()
            lat = '<MISSING>'
            lng = '<MISSING>'
            hour = '<MISSING>' 
            
        store =[]
        
        store.append(domain_url)
        store.append(location_name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append('US')
        store.append('<MISSING>')
        store.append(phone)
        store.append('<MISSING>')
        store.append(lat)
        store.append(lng)
        store.append(hour)
        store.append(base_url)
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
