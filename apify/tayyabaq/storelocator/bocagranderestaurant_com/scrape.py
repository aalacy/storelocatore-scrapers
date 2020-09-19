import csv
import os
import re, time
import requests
import usaddress
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "page_url","location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def fetch_data():
    stores_text=[];data=[]; latitude=[];longitude=[];zipcode=[];location_name=[];city=[];street_address=[]; state=[]; phone=[];hours_of_operation=[]
    url ="http://bocagranderestaurant.com/contact-us/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    location = soup.findAll("div", {"class": "row tm_pb_row tm_pb_row_1"})
    stores=[location[n].get_text() for n in range(0,len(location))]
    for n in range(0,len(stores)):
        a = stores[n].split("\n")
        for m in range(0,len(a)):
            if (a[m]!="") and (a[m]!=[]) and (a[m]!=' '):
                stores_text.append(a[m])
    for n in range(0,len(stores_text),5):
        location_name.append(stores_text[n])
    for n in range(1,len(stores_text),5):
        street_address.append(stores_text[n])
    for n in range(2,len(stores_text),5):
        city.append(stores_text[n].split(",")[0])
        state.append(stores_text[n].split(",")[1].strip().split()[0])
        tagged = usaddress.tag(stores_text[n])[0]
        try:
            zipcode.append(tagged['ZipCode'])
        except:
            zipcode.append('<MISSING>')
    for n in range(3,len(stores_text),5):
        phone.append(stores_text[n])
    for n in range(4,len(stores_text),5):
        hours_of_operation.append(stores_text[n].replace('\u2013',''))
    for n in range(0,len(location_name)): 
        data.append([
            'http://bocagranderestaurant.com',
            'http://bocagranderestaurant.com/contact-us/',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>',
            hours_of_operation[n]
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
