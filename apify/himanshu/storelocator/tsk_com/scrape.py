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
    base_url = "https://tsk.com"
    return_main_object = []
    r = session.get(base_url+'/locations/')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{"class":"loc-full-st"}).find_all('div',{"class":"loc-fullbox"})
    for atag in main:
        link=atag.find('a')['href']
        r1 = session.get(link)
        soup1=BeautifulSoup(r1.text,'lxml')
        phone=''
        address=''
        city=''
        state=''
        zip=''
        lat=''
        lng=''
        country="US"
        name=soup1.find('h2',{'itemprop':'name'}).text.strip()
        if soup1.find('div',{"class":"address-info"}).find('span',{"itemprop":"streetAddress"})!=None:
            address=soup1.find('div',{"class":"address-info"}).find('span',{"itemprop":"streetAddress"}).text.replace(',',' ').strip()
        if soup1.find('div',{"class":"address-info"}).find('span',{"itemprop":"addressLocality"})!=None:
            city=soup1.find('div',{"class":"address-info"}).find('span',{"itemprop":"addressLocality"}).text.replace(',',' ').strip()
        if soup1.find('div',{"class":"address-info"}).find('span',{"itemprop":"addressRegion"})!=None:
            state=soup1.find('div',{"class":"address-info"}).find('span',{"itemprop":"addressRegion"}).text.strip()
        if soup1.find('div',{"class":"address-info"}).find('span',{"itemprop":"postalCode"})!=None:
            zip=soup1.find('div',{"class":"address-info"}).find('span',{"itemprop":"postalCode"}).text.strip()
        if soup1.find('a',{"itemprop":"telephone"})!=None:
            phone=soup1.find('a',{"itemprop":"telephone"}).text.replace('Phone: ','').strip()
        hour=''
        if soup1.find('time',{"itemprop":"openingHours"})!=None:
            for hr in soup1.find_all('time',{"itemprop":"openingHours"}):
                hour+=' '.join(list(hr.stripped_strings))
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address.strip() else "<MISSING>")
        store.append(city if city.strip() else "<MISSING>")
        store.append(state if state.strip() else "<MISSING>")
        store.append(zip if zip.strip() else "<MISSING>")
        store.append(country if country.strip() else "<MISSING>")
        store.append("<MISSING>")
        store.append(phone if phone.strip() else "<MISSING>")
        store.append("tsk")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour.strip() else "<MISSING>")
        return_main_object.append(store)                
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
