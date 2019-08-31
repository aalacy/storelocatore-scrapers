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
    
    base_url = "http://lenwich.com/location/"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    
    info =  soup.find_all('div',{"class":"locations-info"})
    for i in info:
        tem_var =[]
        data = list(i.stripped_strings)
        name  = data[0]
        store_name.append(name)
        street_address1 = data[1]
        street_address=street_address1.replace("(212) 787-9368","").replace("(212) 580-8300","").replace("\n","").replace("\r","")
        if "Order" in data[2]:
            phone= street_address1.replace("\n","").replace("469 Columbus Ave","").replace("469 Columbus Ave","302 Columbus Ave").replace("\r","")
        else:
            phone =  data[2]
        
        hours = ''
        if len(data)==7:
            if "Mon – Fri : 6am – 8pm" in data[4]:
                hours = data[4] + ' '+data[5]  + ' '+data[6]
            else:
                hours = hours + data[5]   +' '+  data[6]
        elif len(data)==8:
            hours = hours + data[5]   +' '+  data[6] + ' '+ data[7]
        elif len(data)==9:
            hours = hours + data[5]   +' '+  data[6] + ' '+ data[7] + ' '+data[8]
            
        elif len(data)==6:
            hours = hours + data[4]   +' '+  data[5] 
        tem_var.append(street_address)
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append("US")
        tem_var.append("<MISSING>")
        tem_var.append(phone.replace("302 Columbus Ave",""))
        tem_var.append("lenwich")
        tem_var.append("<MISSING>")
        tem_var.append("<MISSING>")
        tem_var.append(hours)
        store_detail.append(tem_var)

    for i in range(len(store_name)):
        store =list()
        store.append("http://lenwich.com/location/")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)
    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
