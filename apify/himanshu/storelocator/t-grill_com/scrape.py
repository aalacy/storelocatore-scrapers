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
    base_url ="http://t-grill.com"
    return_main_object=[]
    r = session.get(base_url+'/locations/')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',id="container-mid-inner").find('table').find_all('tr')
    # print(len(main))
    i=0
    ph=[]
    nm=[]
    ad=[]
    ct=[]
    for tag in main:
        if tag.find('td')!=None:
            if i>0:
                for val in tag.find_all('td'):
                    if val.text:
                        if i==1:
                            nm.append(val.text)
                        if i==2:
                            add=list(val.stripped_strings)
                            ad.append(add[0])
                            ct.append(add[1])
                        if i==3:
                            ph.append(val.text)
            i=i+1
            if i==4:
                i=0
    for i in range(len(nm)):
        name=nm[i]
        address=ad[i].strip()
        phone=ph[i].replace('435-67FRESH (','').replace(')','').replace('(','')
        ctt=ct[i].strip().split(' ')
        zip=ctt[-1].strip()
        del ctt[-1]
        if ctt[-1]=='':
            del ctt[-1]
        state=ctt[-1].replace('.','').strip()
        del ctt[-1]
        city=' '.join(ctt).replace(',','').strip()
        lat=''
        lng=''
        storeno=''
        hour=''
        country='US'
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
        store.append("<MISSING>")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour.strip() else "<MISSING>")
        store.append('http://t-grill.com/locations/')
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
