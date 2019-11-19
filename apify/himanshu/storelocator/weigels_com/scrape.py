import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import unicodedata

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url","raw_address"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://weigels.com"
    r = requests.get(base_url+"/location/")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"class":"location-list"}).find_all('div',{'class':"location"})
    for loc in main:
        lat=loc['data-lat']
        zip="<MISSING>"
        lng=loc['data-lng']
        name=loc.find('div',{"class":"locationInfo"}).find('h4').text.strip()
        storeno=loc.find('div',{"class":"locationInfo"}).find('h4').text.strip().split(' ')[-1]
        hour=' '.join(list(loc.find('div',{"class":"locationInfo"}).find('div',{'class':"locationHours"}).stripped_strings)).replace('Hours:','').strip()
        madd=loc.find('div',{"class":"locationInfo"}).find('div',{'class':"locationAddress"}).text.strip()
        phone=loc.find('div',{"class":"locationInfo"}).find('div',{'class':"locationPhone"}).text.strip()
        store=[]
        store.append(base_url)
        store.append(name)
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("<INACCESSIBLE>")
        store.append("US")
        store.append(storeno)
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        if hour.strip():
            store.append(hour.strip())
        else:
            store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(madd)
        for i in range(len(store)):
            if type(store[i]) == str:
                store[i] = ''.join((c for c in unicodedata.normalize('NFD', store[i]) if unicodedata.category(c) != 'Mn'))
        store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
        store = [x if x else "<MISSING>" for x in store]
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
