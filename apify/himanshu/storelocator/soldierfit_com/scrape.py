import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://soldierfit.com/"
    return_main_object=[]
    r = requests.get(base_url)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{"class":"ubermenu-submenu-id-12020"}).find_all('li')
    for dt in main:
        link=dt.find('a')['href']
        r1 = requests.get(base_url+link)
        soup1=BeautifulSoup(r1.text,'lxml')
        if len(soup1.find_all('script',type="application/ld+json"))>1:
            loc=json.loads(soup1.find_all('script',type="application/ld+json")[-1].text)
            address=loc['address']['streetAddress'].strip()
            city=loc['address']['addressLocality'].strip()
            state=loc['address']['addressRegion'].strip()
            zip=loc['address']['postalCode'].strip()
            country=loc['address']['addressCountry'].strip()
            lat=loc['geo']['latitude']
            lng=loc['geo']['longitude']
            name=loc['name']
            phone=loc['telephone']
        else:
            mdd=list(dt.find('table').stripped_strings)
            if mdd[0]==">":
                del mdd[0]
            address=mdd[1].strip()
            country="US"
            city=mdd[0].split(',')[0].strip()
            state=mdd[0].split(',')[1].replace(".",'').strip()            
            zip=''
            if len(mdd[2].split(' '))>1:
                try:
                    zip=int(mdd[2].split(' ')[-1])
                except:
                    zip=''
            name=soup1.find('div',{"class":"title"}).text.strip()
            phone=mdd[3].strip()
            lng=soup1.find('iframe')['src'].split('!2d')[1].split('!')[0].strip()
            lat=soup1.find('iframe')['src'].split('!3d')[1].split('!')[0].strip()
            
        hour=''
        hour=' '.join(soup1.find('div',{'class':"time-hour"}).stripped_strings)
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
        store.append("soldierfit")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour.strip() else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
