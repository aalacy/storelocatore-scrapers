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
    base_url = "https://www.vervecoffee.com"
    r = session.get(base_url+'/pages/locations')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('section',{"class":'image-square'})
    for atag in main:
        loc=list(atag.find('div',{"class":"content"}).stripped_strings)
        name=atag.find('div',{"class":"content"}).find('h6').text.strip()
        if atag.find('div',{"class":"content"}).find('span',{"itemprop":"streetAddress"})!=None:
            address=atag.find('div',{"class":"content"}).find('span',{"itemprop":"streetAddress"}).text.strip()
        else:
            address="<MISSING>"
        if atag.find('div',{"class":"content"}).find('span',{"itemprop":"addressLocality"})!=None:
            city=atag.find('div',{"class":"content"}).find('span',{"itemprop":"addressLocality"}).text.strip()
        else:
            city="<MISSING>"
        if atag.find('div',{"class":"content"}).find('span',{"itemprop":"addressRegion"})!=None:
            state=atag.find('div',{"class":"content"}).find('span',{"itemprop":"addressRegion"}).text.strip()
        else:
            state="<MISSING>"
        if atag.find('div',{"class":"content"}).find('span',{"itemprop":"postalCode"})!=None:
            zip=atag.find('div',{"class":"content"}).find('span',{"itemprop":"postalCode"}).text.strip()
        else:
            zip="<MISSING>"
        if atag.find('div',{"class":"content"}).find('p',{"itemprop":"telephone"})!=None:
            phone=atag.find('div',{"class":"content"}).find_all('p',{"itemprop":"telephone"})[-1].text.replace('Office:','').strip()
        else:
            phone="<MISSING>"
        lat="<MISSING>"
        lng="<MISSING>"
        hour=loc[-3].strip()
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
        store.append("vervecoffee")
        store.append(lat)
        store.append(lng)
        store.append(hour)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
