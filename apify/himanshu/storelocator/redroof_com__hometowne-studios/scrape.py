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
    base_url = "https://www.redroof.com"
    return_main_object=[]
    r = requests.get(base_url+'/hometowne-studios')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find_all('a',href=re.compile("^/extendedstay/hometownestudios/property"))
    for dt in main:
        r1 = requests.get(base_url+dt['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('div',{'class':'hts-property-detail'})
        storeno=dt['href'].split('/')[-1].strip()
        country=main1.find('meta',{'property':'s:addressCountry'})['content'].strip()
        address=main1.find('meta',{'property':'s:streetAddress'})['content'].strip()
        city=main1.find('meta',{'property':'s:addressLocality'})['content'].strip()
        state=main1.find('meta',{'property':'s:addressRegion'})['content'].strip()
        zip=main1.find('meta',{'property':'s:postalCode'})['content'].strip()
        lat=''
        lng=''
        name=main1.find('span',{'property':'s:name','class':'hotel-sector'}).text.strip()
        hour=''
        hr=list(main1.find('div',{"class":'c-content-block__main'}).stripped_strings)
        phone=hr[-1].strip()
        del hr[-1]
        del hr[-1]
        hour=' '.join(hr)
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
        store.append("redroof")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour.strip() else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
