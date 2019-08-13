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
    header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
    return_main_object = []
    base_url = "https://www.additionfi.com/"
    location_url  = 'https://www.additionfi.com/RestApi/locations?type=Branches&format=json'
    r = requests.get(location_url ,headers = header).json()
    for idx, val in enumerate(r):
        
        r = requests.get(base_url+'locations-hours/detail/'+val['UrlName'],headers = header)
        soup = BeautifulSoup(r.text,"lxml")
       
        locator_domain = base_url
        location_name = val['Title']
        v = soup.find('div',{'class':'address'}).text.strip()
       
        street_address = v.split('\n')[0].strip()
       
        city = v.split('\n')[1].strip().split(',')[0].strip()
        state = v.split('\n')[1].strip().split(',')[1].strip().split(' ')[0].strip()
        zip = v.split('\n')[1].strip().split(',')[1].strip().split(' ')[1].strip()
        
        store_number = '<MISSING>'
        country_code = 'US'
        phone = val['Phone']
        location_type = 'additionfi'
        latitude = '<MISSING>'
        longitude = '<MISSING>'
        hours_of_operation = soup.find('div',{'class':'hours-spreadsheet'}).find_all('div',{'class':'hours-row'})
        cc= []
        for vv in hours_of_operation:
           
            cc.append(vv.find('div',{'class':'days'}).text+vv.find_all('div',{'class':'times'})[0].text+vv.find_all('div',{'class':'times'})[1].text)
        
        
        hours_of_operation = 'Lobby - Drive-up :'+''.join(cc)
       

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
