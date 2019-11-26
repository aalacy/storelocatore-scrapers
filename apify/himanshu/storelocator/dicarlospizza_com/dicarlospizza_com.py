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
  
    hours = []
    store_name=[]
    store_detail=[]
    phone=[]
    return_main_object=[]
    address=[]
    k = (soup.find_all("div",{"class":"sqs-block-content"}))

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


            # tem_var.append("https://www.dicarlospizza.com")
            store_name.append(name.replace("*",""))
            tem_var.append(st)
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("dicarlospizza")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            # if tem_var[3] in address:
            #     continue
        
            # address.append(tem_var[3])

            store_detail.append(tem_var)
   
    del store_name[5]
    del store_detail[5]
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.dicarlospizza.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        # if store[3] in address:
        #         continue
        
        # address.append(store[3])

        return_main_object.append(store) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()




