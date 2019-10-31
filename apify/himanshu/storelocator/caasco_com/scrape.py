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
    get_url ='https://www.caasco.com/store-locator'
    domain_url = 'https://www.caasco.com/'
    

    r = requests.get(get_url, headers=headers)    
    soup = BeautifulSoup(r.text, "lxml")    
    # print(soup)
    main =soup.find("input", {'id': 'locations'})['value']

    json_obj = json.loads(main)
    for i in json_obj:
        location_name =i['name']
        address = i['address']
        city =i['city']
        state= 'ON'
        zip=i['postal']
        phone= i['phone']
        lat= i['lat']
        lng=i['lng']
        hour= 'Monday' +' '+i['hours1']+' '+'Tuesday' +' '+i['hours2']+' '+'Wednesday' +' '+i['hours3']+' '+'Thursday' +' '+i['hours4']+' '+'Friday' +' '+i['hours5']+' '+'Saturday' +' '+i['hours6']+' '+'Sunday' +' '+i['hours7']       
        tem_var=[]       
        tem_var.append(domain_url)
        tem_var.append(location_name)
        tem_var.append(address)
        tem_var.append(city)
        tem_var.append(state) 
        tem_var.append(zip)
        tem_var.append('CA')
        tem_var.append("<MISSING>")
        tem_var.append(phone)
        tem_var.append("<MISSING>")
        tem_var.append(lat)
        tem_var.append(lng)
        tem_var.append(hour)
        tem_var.append('<MISSING>') 
        return_main_object.append(tem_var)
        
           
 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
