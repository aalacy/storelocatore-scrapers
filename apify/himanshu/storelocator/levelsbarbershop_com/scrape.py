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
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36'
        }
    base_url= "https://www.levelsbarbershop.com/locations.html"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    hours =[]
    phone =[]
    
    k = (soup.find_all("div",{"class":"paragraph"}))
    k1  = soup.find_all("h2",{"class":"wsite-content-title"})

    for index,target_list in enumerate(k1):
        tem_var =[]
        if (index)<=4:
            store_name.append(target_list.text)
        if index>=5 and index<=8:
           if len(target_list.text.split("ph:")) !=1:
                street_address = (" ".join(target_list.text.split("ph:")[0].split( )[:-2]))
                city  = (target_list.text.split("ph:")[0].split( )[-2].replace(",",""))
                state = (target_list.text.split("ph:")[0].split( )[-1])
                phone = (target_list.text.split("ph:")[-1])


                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append("<MISSING>")
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("levelsbarbershop")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                store_detail.append(tem_var)
           else: 
            store_name.append(target_list.text)

    for target_list in k:

        tem_var =[]
        latitude =''
        longitude =''
        if target_list.a != None:
            latitude = (target_list.a['href'].split("@")[1].split(',')[0])
            longitude = (target_list.a['href'].split("@")[1].split(',')[1])

        if len(target_list.text.split(',')) != 1:
            street_address = (target_list.text.split(',')[0])
            city =(target_list.text.split(',')[1])
            state = (target_list.text.split(',')[2].split(',')[0].replace("\xa0"," ").split("Ph:")[0])
            phone  = (target_list.text.split(',')[2].split(',')[0].replace("\xa0"," ").split("Ph:")[1])

            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.strip())
            tem_var.append("<MISSING>")
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("levelsbarbershop")
            tem_var.append(latitude)
            tem_var.append(longitude)
            tem_var.append("<MISSING>")
            store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.levelsbarbershop.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store) 
        
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
