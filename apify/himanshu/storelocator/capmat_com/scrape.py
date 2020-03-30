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
    base_url = "https://capmat.com"
    r = session.get(base_url+"/Contact.do")
    soup=BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    cnt=0
    main=soup.find('div',{"id":"contactContent"}).find('div',{"class":"row"}).find_all('div',{"class":"row margin-bottom-20"})
    for atag in main:
        loc=list(atag.stripped_strings)
        name=loc[0]
        address=loc[1]
        cnt=cnt+1
        ct=loc[2].split(',')
        if len(ct) == 1:
            address=loc[1]+' '+loc[2]
            ct=loc[3].split(',')
            phone=loc[4].replace('PH:','').strip()
        else:
            phone=loc[3].replace('PH:','').strip()
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[-1].strip()
        hour=re.sub("\s\s+", " ", loc[-1])
        lt=r.text.split('marker'+str(cnt)+' = {')[1].split('{')[1].split('}')[0].split(',')
        lat=lt[0].replace("latitude:",'').strip()
        lng=lt[1].replace("longitude:",'').strip()
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
        store.append("capmat")
        store.append(lat)
        store.append(lng)
        store.append(hour)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
