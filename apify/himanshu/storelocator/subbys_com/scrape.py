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
    base_url = "http://www.subbys.com"
    return_main_object=[]
    r = session.get(base_url+'/locations')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{"id":"content"}).find('div',{"class":"entry"}).find_all('p')
    del main[0]
    del main[0]
    for i in range(len(main)):
        if i%2!=0:
            lat=''
            lng=''
            hr=list(main[i].stripped_strings)
            del hr[-1]
            country="US"
            hour=' '.join(hr).replace('Hours:','')
            storeno=''
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
            store.append("subbys")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour.strip() else "<MISSING>")
            return_main_object.append(store)
        else:
            madd=list(main[i].stripped_strings)
            name=madd[0]
            address=madd[1]
            ct=madd[2].split(',')
            city=ct[0].strip()
            state=ct[1].strip().split(' ')[0].strip()
            zip=ct[1].strip().split(' ')[1].strip()
            phone=madd[-1].replace('Phone:','').strip()
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
