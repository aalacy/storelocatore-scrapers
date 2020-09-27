import csv
import os
import re, time
import requests
from bs4 import BeautifulSoup

def write_output(data):
    line=[]
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row in line:
                continue
            else:
                writer.writerow(row)
                line.append(row)

def fetch_data():
    data=[]; latitude=[];longitude=[];zipcode=[];location_name=[];city=[];street_address=[]; state=[]; phone=[]
    url ="http://www.gosuperpumper.com/station-directory/##"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    location = soup.findAll("td", {"class": "hidden location"})
    location_name=[location[n].get_text() for n in range(0,len(location))]
    address = soup.findAll("td", {"class": "address"})
    street_address = [address[n].get_text().split(",")[0].replace('\xa0',' ') for n in range(0,len(address))]
    state = [address[n].get_text().split(",")[1].split()[0].strip() for n in range(0,len(address))]
    zipcode = [address[n].get_text().split(",")[1].split()[1].strip() for n in range(0,len(address))]
    phones = soup.findAll("td", {"class": "phone"})
    phone = [phones[n].get_text() for n in range(0,len(phones))]
    while("" in phone) :
        phone.remove("")
    lat = soup.findAll("td", {"class": "hidden latitude"})
    latitude = [lat[n].get_text() for n in range(0,len(lat))]
    lng = soup.findAll("td", {"class": "hidden longitude"})
    longitude = [lng[n].get_text() for n in range(0,len(lng))]
    city = location_name
    for n in range(0,len(location_name)): 
        data.append([
            'http://www.gosuperpumper.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            '<MISSING>',
            phone[n],
            '<MISSING>',
            latitude[n],
            longitude[n],
            '<INACCESSIBLE>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
