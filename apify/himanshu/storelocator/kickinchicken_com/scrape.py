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
    base_url = "http://www.kickinchicken.com/"
    r = session.get(base_url+"/locations/")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"class":"locations"}).find_all('a')
    for atag in main:
        if atag['href'].startswith('/locations/'):
            r1 = session.get(base_url+atag['href'])
            soup1=BeautifulSoup(r1.text,'lxml')
            loc=list(soup1.find('div',{'class':'s-locations'}).stripped_strings)
            if len(loc) > 15:
                name=loc[1]
                address=loc[2]
                ct=loc[3].split(',')
                city=ct[0].strip()
                state=ct[1].strip().split(' ')[0].strip()
                zip=ct[1].strip().split(' ')[1].strip()
                phone=loc[4]
                hour=' '.join(list(soup1.find('div',{'class':'hours'}).stripped_strings))
                store = []
                store.append(base_url)
                store.append(name)
                store.append(address)
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append('US')
                store.append("<MISSING>")
                store.append(phone)
                store.append("kickinchicken")
                store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(hour)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
