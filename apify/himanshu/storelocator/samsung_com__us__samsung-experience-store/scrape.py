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
    base_url = "https://www.samsung.com/us/samsung-experience-store"
    r = session.get(base_url+"/locations/")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('div',{"class":"container info-component"})
    for data in main:
        name=data.find('h2',{"class":"info-component-header"}).text.strip()
        mct=list(data.find('h3',{"class":"title"}).stripped_strings)
        address=mct[0].strip()
        ct=mct[1].split(',')
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[1].strip()
        m=list(data.find('div',{"class":"column-content"}).stripped_strings)
        lt=data.find('div',{"class":"column-content"}).find('a',{"class":"header-cta"})['href'].split('@')[1].split(',')
        lat=lt[0]
        lng=lt[1]
        del m[0]
        del m[-1]
        del m[-1]
        del m[1]
        phone=m[0].strip()
        del m[0]
        hour=' '.join(m).strip()
        store=[]
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append("US")
        store.append("<MISSING>")
        store.append(phone)
        store.append("samsung-experience-store")
        store.append(lat)
        store.append(lng)
        store.append(hour)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
