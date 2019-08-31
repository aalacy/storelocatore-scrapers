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
    base_url= "http://elixirjuice.com/all.php"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
  
    store_name=[]
    store_detail=[]
    phone=[]
    return_main_object=[]
    k = (soup.find_all("div",{"class":"abt_main"}))

    for i in k:
        p = i.find_all('div',{"class":"adrs"})
        new = i.find_all('div',{"class":"adrs_nw"})

        for p1 in new:
            tem_var=[]
            st = list(p1.stripped_strings)[0]
            phone = list(p1.stripped_strings)[-1]
            state ="NY"
            city = "<MISSING>"

            
            store_name.append(st)
            tem_var.append(st)
            tem_var.append("<MISSING>")
            tem_var.append(state)
            tem_var.append("<MISSING>")
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone.replace("\n",""))
            tem_var.append("elixirjuice")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            store_detail.append(tem_var)

        for p1 in p:
            tem_var=[]
            
            st = " ".join(list(p1.stripped_strings)[:2]).split(',')[0].replace("corner of greenwich ave and 7th ave","").replace("murray st @ asphalt green bpc","")
         
            if len(" ".join(list(p1.stripped_strings)[:2]).split(','))==2 or len(" ".join(list(p1.stripped_strings)[:2]).split(','))==3:
                state = " ".join(list(p1.stripped_strings)[:2]).split(',')[-1]
            else:
                state = "NY"
            
            phone = (list(p1.stripped_strings)[2].replace("now open!",""))
 
            print(phone)
            store_name.append(st)
            tem_var.append(st)
            tem_var.append("<MISSING>")
            tem_var.append(state)
            tem_var.append("<MISSING>")
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone.replace("\n",""))
            tem_var.append("elixirjuice")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.erewhonmarket.com/")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

