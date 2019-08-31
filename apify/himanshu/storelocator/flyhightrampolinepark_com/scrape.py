# -*- coding: utf-8 -*-
import csv
import requests
from bs4 import BeautifulSoup
import re


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
  
    data = [];
    base_url = 'https://flyhightrampolinepark.com'
    r = requests.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("a", {"class":"btn btnc"})

    for url in links:
      r = requests.get(url["href"])
      soup = BeautifulSoup(r.text, "lxml")
      row = []
      #locator_domain
      row.append(url["href"])
      title = (soup.find("h1", {"class": "title"})).text
      #location_name
      row.append(title.strip())
      address = soup.findAll("address")
    
      logoAltText = soup.find("img", {"class": "logoimg tpf-logo"})['alt']
      if address[1].text.strip() != '':
        addressText = address[1].text.strip()
        #street Address
        row.append(addressText.split(',')[0].strip().split('-')[0])
        #city
        row.append(logoAltText.replace('Fly High', '').strip())
        #state
        row.append((addressText.split(',')[1]).strip().split(' ')[0].strip())
        #zip
        row.append((addressText.split(',')[1]).strip().split(' ')[1].strip())
      else:
        #street Address
        row.append('<MISSING>')
        #city
        row.append('<MISSING>')
        #state
        row.append('<MISSING>')
        #zip
        row.append('<MISSING>')
      
      #country_code
      row.append('US')
      
      #store number
      row.append('<MISSING>')
      
      #phone number
      phoneNumber = (soup.find("div", {"class": "phone"})).text
      row.append(phoneNumber.strip())
    
      #location_type
      row.append('Fly High Trampoline Park')
      
      #longitute
      row.append('<INACCESSIBLE>')
      
      #latitude
      row.append('<INACCESSIBLE>')
      
      #hours_of_operation
      
      timeDiv = soup.find("div", {"class": "time"})
      
      if timeDiv != None:
        hourLink = timeDiv.findChildren("a")[0]
        
        hours = []
        hour_r = requests.get(hourLink["href"])
        hour_soup = BeautifulSoup(hour_r.text, "lxml")
        reg_hours = hour_soup.find('strong', string=re.compile(r'^Regular'))
        ul = reg_hours.findNext('ul')
        for hour in ul.findChildren('li'):
          hours.append(hour.text)
        row.append(','.join(hours))
      else:
        row.append('<MISSING>')
        
      data.append(row)
        
    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
