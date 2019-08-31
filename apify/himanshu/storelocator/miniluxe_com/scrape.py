import csv
import requests
from bs4 import BeautifulSoup
import re

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
    base_url = "https://miniluxe.com/"
    loacation_url = base_url+'locations/'
    r = requests.get(loacation_url, headers = header)
    soup = BeautifulSoup(r.text,"lxml")
    
    d = soup.find("div",{"class": "row_locations"}).find_all('div',{'class':'location'})
    
    for target_list in d:
        gethref = target_list.find('a',{'class':'location_more'})['href']
        k = requests.get(gethref, headers = header)
        soup = BeautifulSoup(k.text,"lxml")
        locator_domain = base_url
        location_name = soup.find('h1').text
        street_address = soup.find('div',{'class':'location_address'}).text
        v = soup.find('div',{'class':'location_city'}).text
        g = v.strip().split(',')
        city = g[0]        
        state = g[1]
        zip = '<MISSING>'
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = 'miniluxe'
        latitude =  '<MISSING>'
        longitude =  '<MISSING>'
        phone = soup.find('div',{'class':'location_phone'}).find('a').text
        j = list(soup.find('div',{'class':'single-location'}).find_all('div',{'class':'col-sm-6'})[1].stripped_strings)
        j.pop(0)
        hours_of_operation = ' '.join(j)
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
