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
    base_url= "http://topsbarbq.com/locations/"
    r = requests.get(base_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")
    store_name=[]
    store_detail=[]
    return_main_object=[]
    phone = []
    k = soup.find_all("div",{"class":"entry-content"})
    for target_list in k:
        p =target_list.find_all("div",{"class":"et_pb_text_inner"})
        for p1 in p:
            tem_var =[]
            if len(list(p1.stripped_strings))==7:
                store_name.append(list(p1.stripped_strings)[0])
                street_address = list(p1.stripped_strings)[2].split(',')[0]
                city = list(p1.stripped_strings)[2].split(',')[1]
                state=list(p1.stripped_strings)[2].split(',')[2].split( )[0]
                zipcode = list(p1.stripped_strings)[2].split(',')[2].split( )[1]

                phone = (list(p1.stripped_strings)[6])
        
                hours =  (list(p1.stripped_strings)[4])

                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state.strip())
                tem_var.append(zipcode.strip())
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone)
                tem_var.append("topsbarbq")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hours)
                store_detail.append(tem_var)
    
    for i in range(len(store_name)):
        store = list()
        store.append("http://topsbarbq.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
                    
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()

