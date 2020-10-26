# coding=UTF-8

import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json



session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://boomerjacks.com"
    link = "https://boomerjacks.com/wp-json/wpgmza/v1/marker-listing/base64eJyrVirIKHDOSSwuVrJSCg9w941yjInxTSzKTi3yySwuycxLj4lxL8pMUdJRKi5JLCpRsjLQUcpJzUsvyVCyMjLVUcpNLIgHSlspGSnVAgD-Vxkm"
    r = session.get(link, headers=headers)
    json_data = r.json()
    locator_domain = base_url
    location_name = ""
    street_address = ""
    city = ""
    state = ""
    zipp = ""
    country_code = "US"
    store_number = ""
    phone = ""
    location_type = ""
    latitude = ""
    longitude = ""
    hours_of_operation = ""
    page_url =''
    city1 =''
    for location in json_data['meta']:
        # print(location['address'])


        # phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(str_data))
        us_zip_list = re.findall(re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(location['address']))
        state_list = re.findall(r' ([A-Z]{2})', str(location['address']))
        latitude =  location['lat']
        longitude = location['lng']
        description = location['description']

        location_name = location['title']
        phone_list1 = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(description))
 
        phone_list = re.findall(re.compile(".?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).?"), str(description.split("<br")[0].split("F")[0]))
        phone = phone_list[-1]
        
        soup1= BeautifulSoup(description,"lxml")
        hours_of_operation = (soup1.text.replace(phone_list1[0],"").replace(phone_list1[-1],"").split("Store")[0].replace("Patio, dog friendly","").replace(". CalendarMore InfoOrder Online","").replace("Dog friendly","").replace("P F ","").encode('ascii', 'ignore').decode('ascii').strip().replace("P   F ","").replace("P   F ","").replace(". Calendar","").replace(".  Calendar","").replace("Live"," Live").replace("P  ","").replace("F ",""))

        if us_zip_list:
            zipp = us_zip_list[-1]
            country_code = "US"


        if state_list:
            state = state_list[-1]
        
        city_add = location['address'].replace(state,"").replace(zipp,"")
        if len(city_add.split("Dr."))==2:
            city = city_add.split("Dr.")[-1].replace("Texas","")
        else:
            kp = location['address'].replace(state,"").replace(zipp,"").strip().lstrip().split(",")
            if kp[-1]=='':
                del kp[-1]
            if kp[-1]==" Texas":
                del kp[-1]
            city = (kp[-1].replace("158 W FM 544 Murphy","").replace("201 West State Highway 114 ","").replace("131 E Stacy Rd ","").replace("6155 Samuell Blvd ","").strip())

        street_address = location['address'].replace(state,"").replace(zipp,"").split(",")[0].replace(city1,"")
        
        
      
        store = [locator_domain, location_name, street_address, city, state.replace("SW","Texas"), zipp, country_code,
                    str(store_number), str(phone), location_type, str(latitude), str(longitude), hours_of_operation,page_url]

        if str(store[2]) + str(store[-3]) not in addresses:
            addresses.append(str(store[2]) + str(store[-3]))

            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        
            yield store

        # hp=[]
        # return hp 

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
