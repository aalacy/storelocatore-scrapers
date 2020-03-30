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
    base_url = "https://www.alibertos.com"
    return_main_object=[]
    r = session.get(base_url+'/locations')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find_all('div',{"class":"collection-item"})
    for dt in main:
        link=dt.find('a',{'class':'link-block-3'})['href']
        phone=dt.find('div',{'class':'text-block-12'}).text.strip()
        r1 = session.get(base_url+link)
        soup1=BeautifulSoup(r1.text,'lxml')
        name=soup1.find('h1',{'class':'heading-54'}).text.strip()
        madd=list(soup1.find('div',{"class":"rich-text-block-2"}).stripped_strings)
        if len(madd)>1:
            address=madd[0].strip()
            ct=madd[1].split(',')
            city=ct[0].strip()
            st=ct[1].strip().split(' ')
            state=st[0].strip()
            zip=''
            if len(st)>1:
                zip=st[1].strip()
        else:
            mad=madd[0].split(',')
            md=mad[0].strip().split(' ')
            city=md[-1]
            del md[-1]
            address=' '.join(md).strip()
            st=mad[1].strip().split(' ')
            state=st[0].strip()
            zip=''
            if len(st)>1:
                zip=st[1].strip()
        hour=''
        store=[]
        storeno=''
        lat=''
        lng=''
        country="US"
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("alibertos")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour.strip() else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
