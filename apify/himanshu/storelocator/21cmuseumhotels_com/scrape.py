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
    base_url ="https://www.21cmuseumhotels.com"
    return_main_object=[]
    r = session.get(base_url)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('nav',{"class","nav-footer"}).find('a',text='Locations').parent.find('ul').find_all('a')
    for tag in main:
        r1 = session.get(tag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        if soup1.find('section',{"id":'contact'})!=None:
            main1=soup1.find('section',{"id":'contact'}).find('div',{"class":"col-sm-4"})
            madd=list(main1.find('p',{"class":"emphasis"}).stripped_strings)
            name=madd[0].strip()
            address=madd[1].strip()
            ct=madd[2].split(',')
            city=ct[0].strip()
            st=ct[1].strip().split(' ')
            zip=st[-1].strip()
            del st[-1]
            state=' '.join(st).strip()
            phone=soup1.find('dl',{"class":'contact-numbers'}).find('dd').text.strip()
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
            store.append("21cmuseumhotels")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour.strip() else "<MISSING>")
            return_main_object.append(store)   
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
