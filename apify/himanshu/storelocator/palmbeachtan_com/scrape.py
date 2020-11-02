import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('palmbeachtan_com')




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
    base_url = "https://palmbeachtan.com"
    r = session.get(base_url+'/locations/states/')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{"class":"state-list"}).find_all('a')
    for atag in main:
        r1 = session.get(base_url+atag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('section',{"id":"content"}).find('div',{'class':"copy"}).find_all('a')
        for atag1 in main1:
            logger.info(atag['href'])
            r2 = session.get(base_url+atag['href']+atag1['href'])
            soup2=BeautifulSoup(r2.text,'lxml')
            address=''
            city=''
            state=''
            zip=''
            phone=''
            name=soup2.find('div',{'class':"location-info"}).parent.find('h1').text.strip()
            if soup2.find('data',{"itemprop":"streetAddress"})!=None:
                address=soup2.find('data',{"itemprop":"streetAddress"}).text.strip()
            if soup2.find('data',{"itemprop":"addressLocality"})!=None:
                city=soup2.find('data',{"itemprop":"addressLocality"}).text.strip()
            if soup2.find('data',{"itemprop":"addressRegion"})!=None:
                state=soup2.find('data',{"itemprop":"addressRegion"}).text.strip()
            if soup2.find('data',{"itemprop":"postalCode"})!=None:
                zip=soup2.find('data',{"itemprop":"postalCode"}).text.strip()
            if soup2.find('data',{"itemprop":"telephone"})!=None:
                phone=soup2.find('data',{"itemprop":"telephone"}).text.strip()
            hour=''
            if soup2.find('aside',{"class":"hours"})!=None:
                  hour=' '.join(list(soup2.find('aside',{"class":"hours"}).stripped_strings)).strip()
            lt=soup2.find('address',{"itemprop":"address"}).find('a')['href'].split('=')[-1].split(',')
            lat=lt[0]
            lng=lt[1]
            storeno=''
            country="US"
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
            store.append("palmbeachtan")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour.strip() else "<MISSING>")
            yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
