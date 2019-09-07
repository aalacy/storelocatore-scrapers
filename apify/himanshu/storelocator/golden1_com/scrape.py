import csv
import requests
from bs4 import BeautifulSoup
import re
import json


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5','Content-type':'application/x-www-form-urlencoded'}
    return_main_object = []
    base_url = "https://www.golden1.com/"
    data  = "lat=38.57933&lng=-121.49089800000002&searchby=FCS%7C&SearchKey=&rnd=1566557208502"
    location_url  = 'https://golden1.locatorsearch.com/GetItems.aspx'
    r = requests.post(location_url ,headers = header, data = data)
   
    soup = BeautifulSoup(r.text,"html.parser")
    for idx,v in enumerate(soup.find_all('marker')):
        
       

        latitude = v['lat']
        longitude = v['lng']
        locator_domain =  base_url
        location_name = v.find('label').text.replace('<br>','')
        street_address = v.find('add1').text.replace('<br>','')
        vk = v.find('add2').text.split(',')
        city = vk[0].strip()
        state = vk[1].strip().split(' ')[0]
        zip = vk[1].strip().split(' ')[1]
        country_code = 'USA'
        store_number = '<MISSING>'
        phone = '<MISSING>'
        location_type = 'golden1'
        hours_of_operation = v.find('contents').text.split('><')[-1].split('<br>')[0].strip().replace('div>','').replace('<br />','').replace('No-Envelope ATM Available</','').replace('</','')
        
        store=[]
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip if zip else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        
        store.append(hours_of_operation  if hours_of_operation else '<MISSING>')
        
        
        return_main_object.append(store)  
       

    return return_main_object         
    
    


def scrape():
    data = fetch_data()

    write_output(data)

scrape()
