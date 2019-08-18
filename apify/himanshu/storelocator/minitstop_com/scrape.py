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
    
    base_url = "https://hawaiipetroleum.com/locations/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    info = soup.find_all("div",{"class":"wpgmza-content-address-holder"})

    for i in info:
        tem_var=[]
        if len(list(i.stripped_strings)) ==6:
            store_name.append(list(i.stripped_strings)[0])

            street_address1 = list(i.stripped_strings)[2]
            street_address = street_address1.replace("\n","").split(',')[0]
            city = street_address1.replace("\n","").split(',')[1]
            state =street_address1.replace("\n","").split(',')[2].split( )[0]
            zipcode = street_address1.replace("\n","").split(',')[2].split( )[1]
            hours_of_operation = list(i.stripped_strings)[3]
            phone = list(i.stripped_strings)[4].replace("Tel: ","")

            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("hawaiipetroleum")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours_of_operation)
            
            store_detail.append(tem_var)
            
        elif len(list(i.stripped_strings)) ==4:
            store_name.append(list(i.stripped_strings)[0])
            street_address1 = list(i.stripped_strings)[2].split(',')[0]
            city = list(i.stripped_strings)[2].split(',')[1]
            state = list(i.stripped_strings)[2].split(',')[2].split( )[0]
            zipcode = list(i.stripped_strings)[2].split(',')[2].split( )[1]
            hours_of_operation ="<MISSING>"
            

            tem_var.append(street_address1)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append("hawaiipetroleum")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours_of_operation)
            store_detail.append(tem_var)
            
            

        elif len(list(i.stripped_strings)) ==5: 
            street_address1 = list(i.stripped_strings)[2]
            store_name.append(list(i.stripped_strings)[0])
            
            hours_of_operation= list(i.stripped_strings)[3]
            if street_address1.count(',') ==3:
                st = street_address1.split(',')
                st[0] = " ".join(st[0:2])
                del st[1]
                street_address = st[0]
                city =st[1]
                state = st[2].split( )[0]
                zipcode = st[2].split( )[1]

                tem_var.append(street_address)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("hawaiipetroleum")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hours_of_operation)
                store_detail.append(tem_var)
                
            else:
                st = street_address1.split(',')[0]
                city =street_address1.split(',')[1]
                state = street_address1.split(',')[2].split( )[0]
                zipcode = street_address1.split(',')[2].split( )[1]

                tem_var.append(st)
                tem_var.append(city)
                tem_var.append(state)
                tem_var.append(zipcode)
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("hawaiipetroleum")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(hours_of_operation)
                store_detail.append(tem_var)
                
                
                

        elif len(list(i.stripped_strings)) ==9:
            
            store_name.append(list(i.stripped_strings)[0])
            hours_of_operation = list(i.stripped_strings)[4]
            street_address = list(i.stripped_strings)[2].split(',')[0]
            city = list(i.stripped_strings)[2].split(',')[1]
            state =list(i.stripped_strings)[2].split(',')[2].split( )[0]
            zipcode =list(i.stripped_strings)[2].split(',')[2].split( )[1]
            phone = list(i.stripped_strings)[3].replace("Tel: ","")

            tem_var.append(street_address)
            tem_var.append(city)
            tem_var.append(state)
            tem_var.append(zipcode)
            tem_var.append("US")
            tem_var.append("<MISSING>")
            tem_var.append(phone)
            tem_var.append("hawaiipetroleum")
            tem_var.append("<MISSING>")
            tem_var.append("<MISSING>")
            tem_var.append(hours_of_operation)
            store_detail.append(tem_var)
            
    for i in range(len(store_name)):
        store = list()
        store.append("https://hawaiipetroleum.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    # print(return_main_object) 
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
