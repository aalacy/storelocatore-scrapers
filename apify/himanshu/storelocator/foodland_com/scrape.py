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
    store_names=[]
    store_details = []
    hour = []
    for i in range(4):
            base_url = "https://www.foodland.com/store-locations?distance%5Bpostal_code%5D=&distance%5Bsearch_distance%5D=10&distance%5Bsearch_units%5D=mile&field_store_island_value=All&&page="+str(i)
            r = session.get(base_url)
            soup = BeautifulSoup(r.text,"lxml")
            k = soup.find("div",{"class":"item-list"})
            for tr in k.find_all('h3'):
                    url  = "https://www.foodland.com" + tr.a['href'] 
                    r = session.get(url)
                    soup1 = BeautifulSoup(r.text,"lxml")
                    ds = soup1.find_all("div",{"class":"col-xs-12 col-sm"})
                    for i in ds:
                            ds1 =i.find('p')
                            if ds1 != None:
                                    hour.append(ds1.text.replace("Store Hours", ""))
            for tr in k.find_all('h3'):
                    store_names.append(tr.text)
            for index,tr in enumerate(k.find_all('div',{"class":"col-xs-12 col-sm-8"})):
                    temp_var=[]
                    tr1=tr.find_all('div',{"class":"adr" })
                    for data in tr1:
                            data1 = list(data.stripped_strings)
                            if len(data1)==5:
                                    stopwords = 'United States'
                                    data1 = [word for word in data1 if word not in stopwords]
                                    if 'Suite 101' in data1:
                                        stopwords = 'Suite 101'
                                        data1[0] =   data1[0]+ ' '+data1[1]
                                        data1 = [word for word in data1 if word not in stopwords]
                    phone1 = tr.find_all('a')[1].text
                    street_address = data1[0]
                    city = data1[1].split(',')[0]
                    state = data1[2]
                    zipcode = data1[3]
                    country_code = "US"
                    store_number = "<MISSING>"
                    phone =  phone1
                    location_type = "<MISSING>"
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    hours_of_operation = hour[index]
                    temp_var.append(street_address)
                    temp_var.append(city)
                    temp_var.append(state)
                    temp_var.append(zipcode)
                    temp_var.append(country_code)
                    temp_var.append(store_number)
                    temp_var.append(phone)
                    temp_var.append(location_type)
                    temp_var.append(latitude)
                    temp_var.append(longitude)
                    temp_var.append(hours_of_operation)
                    store_details.append(temp_var)
    return_main_object = []
    for i in range(len(store_names)):
            store = list()
            store.append("https://www.foodland.com")
            store.append(store_names[i])
            store.extend(store_details[i])
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()