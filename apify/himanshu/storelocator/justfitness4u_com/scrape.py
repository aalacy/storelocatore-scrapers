import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "http://www.justfitness4u.com/"
    r = session.get(base_url)
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('ul',{"id":"primary-menu"}).find_all("a")
    
    for atag in main:
        if "find-a-gym" in atag['href']:
            r1 = session.get(atag['href'])
            soup1=BeautifulSoup(r1.text,'lxml')
            name=soup1.find('h1',{"class":'entry-title'}).text.strip()
            loc=list(soup1.find('div',{"class":'entry-content'}).find_all('p')[0].stripped_strings)
            address=loc[0].split(',')[0].strip()
            city=loc[0].split(',')[1].strip()
            state=loc[0].split(',')[2].strip().split(' ')[0].strip()
            zip=loc[0].split(',')[2].strip().split(' ')[-1].strip()
            phone=loc[-1]
            hour=' '.join(list(soup1.find('div',{"class":'entry-content'}).find_all('p')[1].stripped_strings))         
            store=[]
            store.append("http://www.justfitness4u.com")
            store.append(name)
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append('US')  
            store.append("<MISSING>")
            store.append(phone)
            store.append("justfitness4u")
            store.append('<MISSING>')
            store.append('<MISSING>')
            store.append(hour)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
