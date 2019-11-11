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
    base_url = "http://thegrandtheatre.com"
    return_main_object=[]
    r = requests.get(base_url+'/search?type=locations')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{"id":"searchresults"}).find_all('a',{"class":"searchtitle"})
    for atag in main:
        r1 = requests.get(base_url+'/'+atag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        name=soup1.find('div',{"id":"theatre"}).find('div',{"class":"title"}).text.strip()
        madd=list(soup1.find('div',{"id":"theatre"}).find('div',{"class":"small"}).stripped_strings)
        print(madd)
        phone=madd[1].replace('Information:','').strip()
        md=madd[0].split('|')
        address=md[0].strip()
        ct=md[1].split(',')
        city=ct[0].strip()
        state=ct[1].strip().split('\xa0')[0].strip()
        zip=ct[1].strip().split('\xa0')[1].strip()
        lat=''
        lng=''
        storeno=atag['href'].split("=")[-1].strip()
        country="US"
        hour=''
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("thegrandtheatre")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
