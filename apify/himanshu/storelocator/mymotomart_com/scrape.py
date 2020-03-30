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
    base_url = "http://mymotomart.com"
    r = session.get(base_url+"/Locations")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"id":"dnn_RightPane"}).find_all('div',{"class":"highrow"})
    for loc in main:
        name=loc.find('div',{"class":"storeNames"}).text.strip()
        if loc.find('div',{"class":"storeAddress"})!=None:
            madd=list(loc.find('div',{"class":"storeAddress"}).stripped_strings)
        else:
            madd=list(loc.find('div',{"class":"storAddress"}).stripped_strings)
        print(madd)
        address=madd[0].strip()
        if len(madd)==4:
            address+=' '+madd[1]
            del madd[1]
        ct=madd[1].strip().split(',')
        city=ct[0].strip()
        state=ct[1].replace('\n',' ').strip().split(' ')[0].strip()
        zip=ct[1].replace('\n',' ').strip().split(' ')[1].strip()
        phone=madd[2].strip()
        country="US"
        hour=''
        lat=loc.find('a')['href'].split('lat=')[1].split('&')[0].strip()
        lng=loc.find('a')['href'].split('lon=')[1].split('&')[0].strip()
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
        store.append("mymotomart")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
