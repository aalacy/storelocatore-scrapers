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
    base_url = "https://urbanplates.com"
    return_main_object=[]
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
    r = session.get(base_url+'/locations/',headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find_all('div',{"class":"locale-thum"})
    for atag in main:
        link=atag.find('a')['href']
        r1 = session.get(link,headers=headers)
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('section',{"id":"main"})
        if main1!=None:
            madd=list(main1.find('div').stripped_strings)
            name=madd[0].strip()
            address=madd[1].strip()
            ct=madd[2].split(',')
            city=ct[0].strip()
            st=ct[1].replace('\xa0\xa0',' ').strip().split(' ')
            state=st[0].strip()
            zip=st[1].strip()
            phone=main1.find('div').find('span').text.strip()
            storeno=''
            lt=main1.find('a',text="Get Directions")['href'].split('@')[1].split(',')
            lat=lt[0].strip()
            lng=lt[1].strip()
            hour=''
            hr=list(main1.find('div',{"class":'storeHours'}).find('div',{'class':"days"}).stripped_strings)
            hr1=list(main1.find('div',{"class":'storeHours'}).find('div',{'class':"hours"}).stripped_strings)
            for i in range(len(hr)):
                hour+=hr[i]+":"+hr1[i]+' '
            store=[]
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
            store.append("urbanplates")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour.strip() else "<MISSING>")
            return_main_object.append(store)
    return return_main_object
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
