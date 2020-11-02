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
    base_url = "https://www.thelagreestudio.com"
    r = session.get(base_url+"/locations.html")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('li',{"class":'menu-locations'}).find('ul',{"class":"dropdown-menu"}).find_all('a')
    for atag in main:
        r1 = session.get(atag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('main',{"id":"main-content"}).find("div",{"class":"editor-content"}).find('div',{"class":"grid-desk-4"}).find_all('p')
        mn=list(soup1.find('main',{"id":"main-content"}).find("div",{"class":"editor-content"}).find('div',{"class":"grid-desk-4"}).stripped_strings)
        name=mn[0]+' '+mn[1]
        lat=main1[2].find('a')['href'].split('/@')[1].split(',')[0]
        lng=main1[2].find('a')['href'].split('/@')[1].split(',')[1]
        del main1[2]
        address=list(main1[0].stripped_strings)[0]
        ct=list(main1[0].stripped_strings)[1].split(',')
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[1].strip()
        phone=list(main1[1].stripped_strings)[0].strip()
        hour=' '.join(list(main1[2].stripped_strings))+","+' '.join(list(main1[3].stripped_strings))+","+' '.join(list(main1[4].stripped_strings))+","+' '.join(list(main1[5].stripped_strings))
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
        store.append("thelagreestudio")
        store.append(lat)
        store.append(lng)
        store.append(hour)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
