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
    base_url= "https://www.redrockcanyongrill.com/locations/"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    hours =[]
    phone =[]

    k = (soup.find_all("div",{"class":"state clearfix"}))

    for i in k:

        a = i.find_all("a")

        for a1 in a:
            time =''
            if "More Info" in a1.text:
                r = requests.get(a1["href"],headers=headers)
                soup1 = BeautifulSoup(r.text,"lxml")
                k1 = (soup1.find_all("div",{"class":"hours clearfix"}))

                for j in k1:
                    time =time+ ' '+ (j.text.replace("\n"," "))
                hours.append(time)
                
      
        st = i.find_all("address",{"class":"half left"})
        phones = i.find_all("p",{"class":"half right"})
        h = i.find_all("h3")
        for h1 in h:
            store_name.append(h1.text)
        for j in phones:
            phone.append(list(j.stripped_strings)[0].replace("Phone: ",""))

        for j in st:
            tem_var =[]
            street_address = (list(j.stripped_strings)[0])
            city = (list(j.stripped_strings)[1].split(',')[0])
            state =  (list(j.stripped_strings)[1].split( )[-2])
            zipcode = (list(j.stripped_strings)[1].split( )[-1])
            
       
            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state.replace(",",""))
            tem_var.append(zipcode)
            store_detail.append(tem_var)

    for i in range(len(store_name)):
        store = list()
        store.append("https://www.redrockcanyongrill.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        store.append("US")
        store.append("<MISSING>")
        store.append(phone[i])
        store.append("redrockcanyongrill")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hours[i])
        return_main_object.append(store)
  
    
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
