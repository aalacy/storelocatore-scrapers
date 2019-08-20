import csv
import os
import requests
import re, time
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='wb') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                #Keep the trailing zeroes in zipcodes
                writer.writerow([unicode(s).encode("utf-8") for s in row])
                
def fetch_data():
    #Variables
    data=[]; store_no=[];location_name=[];location_type=[];city=[];street_address=[]; state=[]; phone=[]
    url ="http://www.speedystop.com/mapservice.php?option=locations"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    stores = soup.find_all('td')
    for i in xrange(0,len(stores),4):
        location_name.append(stores[i].get_text())
        store_no.append(stores[i].get_text().split("#")[1])
    for i in xrange(1,len(stores),4):
        street_address.append(stores[i].get_text().split(",")[0])
        state.append(stores[i].get_text().split(",")[1].strip())
    for i in xrange(2,len(stores),4):
        phone.append(stores[i].get_text())
    for i in xrange(3,len(stores),4):
        if stores[i].get_text()!="":
            location_type.append(stores[i].get_text().split()[-1].strip())
        else:
            location_type.append("<MISSING>")
    for n in range(0,len(location_name)): 
        data.append([
            'http://www.speedystop.com',
            location_name[n],
            street_address[n],
            '<MISSING>',
            state[n],
            '<MISSING>',
            'US',
            store_no[n],
            phone[n],
            location_type[n],
            '<MISSING>',
            '<MISSING>',
            '<MISSING>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
