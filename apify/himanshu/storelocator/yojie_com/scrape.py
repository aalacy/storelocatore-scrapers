import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sys


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
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url= "https://www.yojie.com/locations"
    r = requests.get(base_url,headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    
    k = (soup.find_all("div",{"id":"ctl01_pSpanDesc","class":"t-edit-helper"}))
    return_main_object=[]
    for i in k:
        tem_var =[]
        
        if list(i.stripped_strings) != []:
            if "CONTACT" in list(i.stripped_strings):
                pass
            else:
                name = list(i.stripped_strings)[0]
                st = list(i.stripped_strings)[1]
                city = list(i.stripped_strings)[2].split(',')[0]
                state =  list(i.stripped_strings)[2].split(',')[1].split( )[0]
                zipcode = list(i.stripped_strings)[2].split(',')[1].split( )[1]
                phone  =  list(i.stripped_strings)[3]
                hours = " ".join(list(i.stripped_strings)[4:])

                
                tem_var.append("https://www.yojie.com")
                tem_var.append(name)
                tem_var.append(st)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode.strip())
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("yojie")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hours)
                store_detail.append(tem_var)
               
   
   
    for i in range(len(store_detail)):
        store =list()
        store.extend(store_detail[i])
     
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
