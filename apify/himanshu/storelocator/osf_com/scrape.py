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
    base_url = "https://www.osf.com"
    r = session.get(base_url+'/location/')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('a',{'class':"e-link"})
    for li in main:
        r1 = session.get(li['href'])
        print(li['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        name=soup1.find('h1',{"class":"m-pageHeader_location__title"}).text.strip()
        madd=soup1.find('p',{"class":'m-pageHeader_location__address'}).text.strip().split(',')
        address=madd[0].strip()
        if len(madd)==4:
            address+=" "+madd[1]
            del madd[1]
        city=madd[1].strip()
        country='US'
        lat=''
        lng=''
        state=madd[2].strip().split(' ')[0].strip()
        zip=madd[2].strip().split(' ')[1].strip()
        phone=soup1.find('p',{"class":"m-pageHeader_location__phone"}).text.strip()
        hour=' '.join(list(soup1.find('div',{"class":"m-pageHeader_location__hours"}).stripped_strings))
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("osf")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
