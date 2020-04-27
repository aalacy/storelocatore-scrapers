import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w',newline="") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.tmphysiciannetwork.org"
    return_main_object=[]
    r = session.get(base_url+'/locations')
    soup=BeautifulSoup(r.text,'lxml')
    output=[]
    main=soup.find('ul',{"class":"results"}).find_all('li',{"class":'location'})
    for dt in main:
        name=dt['data-name'].strip()
        lng=dt['data-longitude'].strip()
        lat=dt['data-latitude'].strip()
        city=dt['data-city'].strip()
        state=dt['data-state'].upper()
        zip=dt['data-zip'].strip()
        address=dt['data-address'].strip()+" "+dt["data-address2"].strip()
        storeno=dt['data-loc-id'].strip()
        country="US"
        phone = dt["data-phone"].strip()
         # phone=''
        # if dt.find('p',{"itemprop":"telephone"})!=None:
        #     phone=dt.find('p',{"itemprop":"telephone"}).text
        # link=dt.find('a')['href']
        page_url = base_url+dt["data-domain"].strip()
        r1 = session.get(page_url)
        soup1=BeautifulSoup(r1.text,'lxml')
        hour=''
        if soup1.find('div',{"class":"hours-fax"})!=None:
            hr=list(soup1.find('div',{"class":"hours-fax"}).stripped_strings)
            del hr[0]
            hour=' '.join(hr).strip()
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
        store.append(page_url if page_url else "<MISSING>")
        # if zip not in output:
        #     output.append(zip)
        yield store
        # print(store)
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
