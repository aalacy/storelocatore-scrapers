import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast

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
    base_url= "http://napoleonsbakery.com/locations.php"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    
    data = soup.find_all("div",{"class":"hentry","data-sync":"textbox_content"})
    store_name=[]
    store_detail=[]
    return_main_object=[]

    k = (soup.find_all("div",{"id":"container"}))
    for i in k:
        k1 = i.find_all("li")
        for j in k1:
            tem_var =[]
            tem_var1 = []
            data = list(j.stripped_strings)
            stopwords = "24 hours"
            new_words = [word for word in data if word not in stopwords]
            if len(new_words) != 1 and new_words !=[]:
                store_name.append(new_words[0])
                street_address = (new_words[1])

                
                phone = (new_words[2])



                tem_var.append(street_address.replace("*-","").replace("*","").replace("-","").replace("\u2011",""))
               
                tem_var.append(new_words[0].replace("*-","").replace("*","").replace("-","").replace("\u2011",""))
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("US")
                tem_var.append("<MISSING>")
                
                tem_var.append(phone.replace("\u2011",""))
                
                tem_var.append("napoleonsbakery")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                store_detail.append(tem_var)
            
   
  
   
    for i in range(len(store_name)):
        store = list()
        store.append("http://napoleonsbakery.com")
        store.append(store_name[i].replace("-","").replace("*",""))
        store.extend(store_detail[i])
        return_main_object.append(store) 
        
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

