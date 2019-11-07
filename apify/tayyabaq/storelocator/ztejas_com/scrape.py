import csv
import os
import re, time
import requests
from bs4 import BeautifulSoup
import lxml.html
import usaddress

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain","page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)

def fetch_data():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
    data=[];page_url=[];hours_of_operation=[]; latitude=[];longitude=[];zipcode=[];location_name=[];city=[];street_address=[]; state=[]; phone=[]
    url ="https://ztejas.com/locations/"
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, 'html.parser')
    doc = lxml.html.fromstring(r.content)
    location_name = doc.xpath('//nav/a/text()')
    for n in range(0,len(location_name)):
        url = "https://ztejas.com/locations/%s/contact"%location_name[n].replace(" ","-").lower()
        page_url.append(url)
        r=requests.get(url)
        doc1 = lxml.html.fromstring(r.content)
        store = doc1.xpath('//div[@class="grid-x"]/div[1]/p[2]/text()')
        print (store)
        tagged =usaddress.tag(' '.join(store).replace("Phone:",""))[0]
        street = ' '.join(store).replace("Phone:","").split(",")[0].split("\n")
        if street[0][0].isdigit()==True:
            street_address.append(' '.join(street))
        else:
            street_address.append(' '.join(street[1:]))
        phone.append(doc1.xpath('//a[contains(@href,"tel")]/text()')[0])
        city.append(tagged['PlaceName'])
        state.append(tagged['StateName'])
        zipcode.append(tagged['ZipCode'])
        hours_of_operation.append(str("Monday "+' '.join(doc1.xpath('//div[@class="grid-x"]/div[1]/p/text()')).split("Monday")[1].strip()))
    for n in range(0,len(location_name)): 
        data.append([
            'https://ztejas.com',
            page_url[n],
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
