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
    base_url = "https://theboilingcrab.com"
    return_main_object=[]
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
    r = session.get(base_url,headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    output=[]
    main=soup.find('div',{"id":"locations"}).find('div',{'class':"fusion-column-wrapper"}).find_all('a')
    for atag in main:
        link=atag['href']
        r1 = session.get(link,headers=headers)
        soup1=BeautifulSoup(r1.text,'lxml')
        madd=list(soup1.find('div',{"class":"fusion-blend-mode","class":"1_3"}).find('div',{'class':"fusion-text"}).stripped_strings)
        print(madd)
        name=soup1.find('meta',property="og:title")['content'].split('|')[-1].strip()
        md=madd[1].split(',')
        if len(md)>2:
            address=md[0].strip()
            city=md[1].strip()
            state=md[2].strip().split(' ')[0].strip()
            zip=md[2].strip().split(' ')[1].strip()
            del madd[0]
            del madd[0]
            del madd[0]
            del madd[0]
        else:
            address=madd[1].strip()
            ct=madd[2].split(',')
            city=ct[0].strip()
            state=ct[1].strip().split(' ')[0].strip()
            zip=ct[1].strip().split(' ')[1].strip()
            phone=madd[3].strip()
            del madd[0]
            del madd[0]
            del madd[0]
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
