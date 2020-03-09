# coding=UTF-8

import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from datetime import datetime
import time



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

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }

    base_url = "https://www.aarons.com/"

    location_url = "https://api.sweetiq.com/store-locator/public/locations/59151b8997c569e45c00e398?categories=&searchFields%5B0%5D=name"
    r = requests.get(location_url, headers=headers)
    

    json_data = r.json()

    for location in json_data["records"]:
        location_name = location['name']
        street_address = (location['address'] +" "+ location['addressLine2']).strip()
        city = location['city'].capitalize()
        state = location['province']
        zipp = location['postalCode']
        country_code = location['country']
        phone = location['phone']     
        latitude = str(location['geo'][0])
        longitude = str(location['geo'][1])
        page_url = location['website']
        if location['hoursOfOperation']['Mon'] != []:
            Mon_start = datetime.strptime(str(location['hoursOfOperation']['Mon'][0][0]), "%H:%M").strftime("%I:%M %p")
            Mon_close = datetime.strptime(str(location['hoursOfOperation']['Mon'][0][1]), "%H:%M").strftime("%I:%M %p")
            
        else:
            Mon_start = "Close"
            Mon_close = "Close"
        if location['hoursOfOperation']['Tue'] != []:

            Tue_start = datetime.strptime(str(location['hoursOfOperation']['Tue'][0][0]), "%H:%M").strftime("%I:%M %p")
            Tue_close = datetime.strptime(str(location['hoursOfOperation']['Tue'][0][1]), "%H:%M").strftime("%I:%M %p")
        else:
            Tue_start='Close'
            Tue_close='Close'
        if location['hoursOfOperation']['Wed'] != []:

            Wed_start = datetime.strptime(str(location['hoursOfOperation']['Wed'][0][0]), "%H:%M").strftime("%I:%M %p")
            Wed_close = datetime.strptime(str(location['hoursOfOperation']['Wed'][0][1]), "%H:%M").strftime("%I:%M %p")
        else:
            Wed_start='Close'
            Wed_close='Close'
        if location['hoursOfOperation']['Thu'] != []:

            Thu_start = datetime.strptime(str(location['hoursOfOperation']['Thu'][0][0]), "%H:%M").strftime("%I:%M %p")
            Thu_close = datetime.strptime(str(location['hoursOfOperation']['Thu'][0][1]), "%H:%M").strftime("%I:%M %p")
        else:
            Thu_start='Close'
            Thu_close='Close'
        if location['hoursOfOperation']['Wed'] != []:

            Fri_start = datetime.strptime(str(location['hoursOfOperation']['Fri'][0][0]), "%H:%M").strftime("%I:%M %p")
            Fri_close = datetime.strptime(str(location['hoursOfOperation']['Fri'][0][1]), "%H:%M").strftime("%I:%M %p")
        else:
            Fri_start='Close'
            Fri_close='Close'
        if location['hoursOfOperation']['Sat'] != []:
            Sat_start = datetime.strptime(str(location['hoursOfOperation']['Sat'][0][0]), "%H:%M").strftime("%I:%M %p")
            Sat_close = datetime.strptime(str(location['hoursOfOperation']['Sat'][0][1]), "%H:%M").strftime("%I:%M %p")
            
        else:
            Sat_start = "Close"
            Sat_close = "Close"

        if location['hoursOfOperation']['Sun'] != []:
            Sun_start = datetime.strptime(str(location['hoursOfOperation']['Sun'][0][0]), "%H:%M").strftime("%I:%M %p")
            Sun_close = datetime.strptime(str(location['hoursOfOperation']['Sun'][0][1]), "%H:%M").strftime("%I:%M %p")
            
        else:
            Sun_start = "Close"
            Sun_close = "Close"
        hours_of_operation = "Monday"+" "+str(Mon_start)+" "+"to"+" "+str(Mon_close)+" "+\
                            "Tuesday"+" "+str(Tue_start)+" "+"to"+" "+str(Tue_close)+" "+\
                            "Wednesday"+" "+str(Wed_start)+" "+"to"+" "+str(Wed_close)+" "+\
                            "Thursday"+" "+str(Thu_start)+" "+"to"+" "+str(Thu_close)+" "+\
                            "Friday"+" "+str(Fri_start)+" "+"to"+" "+str(Fri_close)+" "+\
                            "Saturday"+" "+str(Sat_start)+" "+"to"+" "+str(Sat_close)+" "+\
                            "Sunday"+" "+str(Sun_start)+" "+"to"+" "+str(Sun_close)
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append("<MISSING>") 
        store.append(phone)
        store.append("<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation.replace("Close to Close","Closed"))
        store.append(page_url)        

        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print("data = " + str(store))
        # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
        yield store



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
