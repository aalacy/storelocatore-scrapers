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
    base_url = "http://nofrillssupermarkets.com/store-location/store-detail"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    return_main_object =[]
    store_detail =[]
    store_name=[]
    tem_var =[]

    k =  soup.find("div",{"class":"location-box","id":"location_one"}).p
    name1 =  soup.find("div",{"class":"location-box","id":"location_one"}).h1
    h =  soup.find("div",{"class":"location-box","id":"location_one"})

    time1 =  list(h.find("div",{"class":"r"}).stripped_strings)
    time = time1[7] + ' ' +time1[9] + ' '+ time1[11] + ' '+time1[13] + ' '+time1[15]
    store_no = name1.text.replace("No Frills ","")
    name = name1.text.replace(" #3803","")
    store_name.append(name)
    phone = list(h.find("div",{"class":"r"}).stripped_strings)[2]
    info = k.text.split(",")
    street_address= info[0]
    city = info[1]
    state = info[2].split( )[0]
    zipcode = info[2].split( )[1]

    tem_var.append(street_address)
    tem_var.append(city)
    tem_var.append(state)
    tem_var.append(zipcode)
    tem_var.append("US")
    tem_var.append(store_no)
    tem_var.append(phone)
    tem_var.append("nofrillssupermarkets")
    tem_var.append("<MISSING>")
    tem_var.append("<MISSING>")
    tem_var.append(time)
    store_detail.append(tem_var)
    
    for i in range(len(store_name)):
        store =list()
        store.append("http://nutritionzoneusa.com")
        store.append(store_name[i])
        store.extend(store_detail[i])
        return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
