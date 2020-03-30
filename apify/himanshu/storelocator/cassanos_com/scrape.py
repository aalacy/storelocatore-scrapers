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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.cassanos.com"
    return_main_object=[]
    r = session.get(base_url+'/online-ordering/')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('article',{"class":'all-locations'}).find_all('a')
    for dt in main:
        r1 = session.get(dt['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        loc=list(soup1.find('address',{'id':'rColAddress'}).stripped_strings)
        name=loc[0].strip()
        storeno=loc[0].split('#')[-1].strip()
        address=loc[1].strip()
        hour=' '.join(soup1.find('div',{'id':'rColHours'}).stripped_strings).strip()
        phone=loc[-1].strip()
        ct=loc[2].split(',')
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[1].strip()
        lat=''
        lng=''
        country="US"
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
        store.append("cassanos")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour.strip() else "<MISSING>")
        store.append("https://www.cassanos.com/online-ordering/")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
