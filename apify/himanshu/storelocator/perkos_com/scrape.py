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
    base_url = "http://perkos.com"
    return_main_object=[]
    r = session.get(base_url+'/locations.html')
    soup=BeautifulSoup(r.text,'lxml')
    output=[]
    main=soup.find('div',{"class":"wrapper_bg01"}).find_all('div',{'class':"box_8"})
    for dt in main:
        if dt.find('h3',{'class':"header"})!=None:
            madd=list(dt.stripped_strings)
            lt=dt.find('h3',{'class':"header"}).find('a')['href'].split('@')[1].split(',')
            lat=lt[0].strip()
            lng=lt[1].strip()
            name=madd[0].strip()
            del madd[0]
            address=madd[0].split('-')[0].strip()
            ct=madd[0].split('-')[1].strip().split(',')
            city=ct[0].strip()
            state=ct[1].strip().split(' ')[0].strip()
            zip=ct[1].strip().split(' ')[1].strip()
            del madd[0]
            del madd[0]
            phone=madd[0].strip()
            del madd[0]
            del madd[0]
            hour=' '.join(madd)
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
            store.append("theboilingcrab")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour.strip() else "<MISSING>")
            if address not in output:
                output.append(address)
                return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
