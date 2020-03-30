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
    base_url = "http://youngsenvironmental.com"
    return_main_object=[]
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',"Content-Type": "application/json; charset=utf-8"}
    r = session.get(base_url+'/contact/',headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{"class":"contact-page-form-google-wrapper"}).find_all('div')
    for atag in main:
        madd=list(atag.stripped_strings)
        print(madd)
        name=madd[0].strip()
        address=madd[1].strip()
        ct=madd[2].split(',')
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[1].strip()
        phone=madd[3].replace('Phone:','').strip()
        lat=atag.find('iframe')['src'].split('!2d')[1].split('!')[0]
        lng=atag.find('iframe')['src'].split('!3d')[1].split('!')[0]
        country="US"
        storeno=''
        hour=''
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
        store.append("youngsenvironmental")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
