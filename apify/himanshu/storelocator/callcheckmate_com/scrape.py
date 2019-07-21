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
    base_url = "https://www.callcheckmate.com"
    r = requests.get(base_url+"/all_locations.php")
    soup=BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    op=soup.find('select',{"class":"lcation_stats"}).find_all('option')
    for atag in op:
        if atag['value']:
            r1 = requests.get(base_url+"/"+atag['value'].lower()+"/all_locations.php")
            soup1=BeautifulSoup(r1.text ,"lxml")
            main=soup1.find('div',{"id":'locationSelect'}).find_all('div',{"class":"add_box"})
            for detail in main:
                loc=list(detail.stripped_strings)
                name=loc[0]
                phone=loc[1]
                address=loc[2]
                city=loc[3].split(',')[0].strip()
                state=loc[3].split(',')[1].strip()
                hour=loc[4]
                zip=detail.find('a',{"class":"directions-lp"})['href'].split('+')[-1].strip()
                store = []
                store.append(base_url)
                store.append(name)
                store.append(address)
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("callcheckmate")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(hour)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
