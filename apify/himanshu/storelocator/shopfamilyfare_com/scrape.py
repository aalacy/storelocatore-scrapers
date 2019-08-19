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
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    for  i  in range(0,10):
        base_url= "https://www.shopfamilyfare.com/locations?page="+str(i)
        r = requests.get(base_url)
        soup= BeautifulSoup(r.text,"lxml")
    
        store_name=[]
        store_detail=[]
        return_main_object=[]
        
        
        k= soup.find_all("div",{"class":"col-xs-12 col-lg-7"})

        for i in k:
            st = i.find_all("div",{"class":"brief"})
            names = i.find_all("h3")

            for name in names:
                store_name.append(name.text.replace("\n",""))
            for j in st:
                tem_var =[]
                address = j.find('p',{"class":"address"})
                phone  = j.find('p',{"class":"phone"}).text.replace("\n","")
                hours = j.find('p',{"class":"hours"}).text.replace("\n","")
                address1 = list(address.stripped_strings)[0]
                city = list(address.stripped_strings)[1].split(',')[0]
                state = " ".join(list(address.stripped_strings)[1].split(',')[1].split( )[:-1])
                zipcode = list(address.stripped_strings)[1].split(',')[1].split( )[-1]
                

                tem_var.append(address1)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("shopfamilyfare")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hours)
                store_detail.append(tem_var)

   
    for i in range(len(store_name)):
        store = list()
        store.append("https://www.shopfamilyfare.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
     
        return_main_object.append(store) 

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
