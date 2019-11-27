import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
  
    base_url= "https://www.dicarlospizza.com/order"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    address12 =[]
    hours = []
    store_name=[]
    store_detail=[]
    phone=[]
    return_main_object=[]
    address=[]
    k = (soup.find_all("div",{"class":"sqs-block-content"}))

    base_url= "https://www.dicarlospizza.com/order"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
  
    for i in k:
        tem_var=[]
        if len(list(i.stripped_strings)) != 1 and list(i.stripped_strings) !=[] :
            if "STEUBENVILLE*" in list(i.stripped_strings)[0]:
                pass
            else:
                name = list(i.stripped_strings)[0]
            phone1 =''
            
            if "Uptown"  in list(i.stripped_strings)[1]:
                pass
            else:
                st = list(i.stripped_strings)[1]

            if "FALL 2019" in list(i.stripped_strings)[2]:
                phone1 = "<MISSING>"
            else:
                phone1 =(list(i.stripped_strings)[2])

            if "Downtown﻿" in phone1:
                pass
            else:
                phone = (phone1)

            store_name.append(name.replace("*",""))
            tem_var.append(st)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            store_detail.append(tem_var)


    jj= []
    k = (soup.find_all("div",{"class":"sqs-col-4"}))
    for x in k:
        for y in x.find_all('div',{'class':'sqs-block-html'}):
            locator_domain  = 'https://www.dicarlospizza.com/'
            location_name = y.find('h3').text.strip()
            street_address = y.find('p')
            cnv  = str(street_address).replace('<br/>','%%')
            jj.append(soup.find_all('script', {'type': 'application/ld+json'}))
            soup = BeautifulSoup(cnv, "lxml")
            street_address = soup.text.split('%%')[0]

            if location_name == 'STEUBENVILLE*':
                db = json.loads(jj[0][2].text)
                street_address = db['address'].split('\n')[0] + ' ' + db['address'].split('\n')[1].strip().split(',')[0]



            phone = ''
            if '.' in soup.text.split('%%')[1]:
                phone  = soup.text.split('%%')[1]
            city = ''
            state = ''
            zip = ''
            country_code = 'US'
            store_number = ''
            location_type = ''
            latitude = ''
            longitude = ''
            hours_of_operation = ''
            page_url = base_url

            store = []
            store_name.append(location_name.replace("*","") if location_name.replace("*","") else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip if zip else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')
            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url if hours_of_operation else '<MISSING>')
            store_detail.append(store)
   
    del store_name[5]
    del store_detail[5]
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.dicarlospizza.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        if store[2] in address12:
            continue
        address12.append(store[2])
   

        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




