import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.regmovies.com"
    r = requests.get(base_url+'/static/en/us/theatre-list')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"class":'cinema-list'}).find_all('a',{"class":"btn-link"})
    for atag in main:
        #print(atag['href'])
        r1 = requests.get(base_url+atag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        name=soup1.find('cinema-structured-data')['data-name'].strip()
        address=soup1.find('cinema-structured-data')['data-address'].strip('[]')
        city=soup1.find('cinema-structured-data')['data-city'].strip()
        state=soup1.find('cinema-structured-data')['data-province'].strip()
        zip=soup1.find('cinema-structured-data')['data-postalcode'].strip()
        phone=soup1.find('cinema-structured-data')['data-telephone'].strip()
        lat=soup1.find('cinema-structured-data')['data-lat'].strip()
        lng=soup1.find('cinema-structured-data')['data-lon'].strip()
        storeno=r1.url.split('/')[-1].strip()
        store=[]
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append(storeno)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        store.append(r1.url)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
