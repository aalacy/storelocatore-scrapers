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
    base_url = "http://timesoil.com"
    return_main_object = []
    headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
    r = session.get(base_url+'/locations/',headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{'class':'elementor-section-wrap'}).find_all('section',{"class":'elementor-element'})
    del main[0]
    for sec in main:
        main1=list(sec.find('div',{'class':'elementor-icon-box-content'}).stripped_strings)
        name=main1[0].strip()
        country="US"
        lat=''
        lng=''
        hour=''
        storeno=name.split('-')[0].strip()
        madd=main1[1].strip().split(',')
        address=re.sub(r'\s+',' ',str(madd[0]))
        state=madd[1].strip().split(' ')[0].strip()
        zip=madd[1].strip().split(' ')[1].strip()
        phone=''
        if sec.find('div',{"class":'elementor-text-editor'})!=None:
            phone=sec.find('div',{"class":'elementor-text-editor'}).find('p').text.strip()
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append("<INACCESSIBLE>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("timesoil")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)                
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
