# -*- coding: utf-8 -*-
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://donsandbens.com"

    r = session.get(base_url)

    soup = BeautifulSoup(r.text,"lxml")

    count = 0

    return_main_object = []

    k = soup.find_all('div',{'class':'team-member'})
    store_name= []
    store_detail =[]

    for i in k:
        for j in i.h4:
            store_name.append(j)
            

    for i in k:
        temp_var = []
        link = i.find_all('div',{'class':'share-social'})

        for j in link:
            data = j.a['href'].split('@')
            
            if len(data) != 1 :
                latitude1  = data[1].split(',')[0]
                longitude1 = data[1].split(',')[1]
            else:
                latitude1 = "<MISSING>"
                longitude1 = "<MISSING>"

        
        for j in i.h6:
            temp = j.replace('•',',').split(',')

            if len(temp)== 4:
                temp[0] = temp[0] + temp[1]
                del temp[1]

        
            street_address = temp[0]
            
            city = temp[1]
            state = temp[2].split( )[0]
            zipcode =  temp[2].split( )[1]
            country_code = "US"
            store_number = "<MISSING>"
            phone = "<MISSING>"
            location_type = "DON'S and BEN'S"
            latitude = latitude1
            longitude = longitude1
            hours_of_operation = "<MISSING>"
        
        
            temp_var.append(street_address.strip())
            temp_var.append(city.strip())
            temp_var.append(state)
            temp_var.append(zipcode)
            temp_var.append(country_code)
            temp_var.append(store_number)
            temp_var.append(phone)
            temp_var.append(location_type)
            temp_var.append(latitude)
            temp_var.append(longitude)
            temp_var.append(hours_of_operation)
            store_detail.append(temp_var)

    main_object = []

    for i  in range(len(store_name)):
        store = list()
        store.append('https://donsandbens.com')
        store.append(store_name[i])
        store.extend(store_detail[i])
        main_object.append(store)

    return main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
