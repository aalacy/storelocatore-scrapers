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
    base_url ="https://www.rogys.com"
    return_main_object=[]
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
    r = requests.get(base_url,headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('li',{"class":'menu-find-your-school'}).find('ul').find_all('a')
    for dt in main:
        r1 = requests.get(dt['href'],headers=headers)
        soup1=BeautifulSoup(r1.text,'lxml')
        hr=list(soup1.find('h4',text="Hours").parent.stripped_strings)
        del hr[0]
        hour=' '.join(hr).strip()
        loc=list(soup1.find('div',{'itemprop':'address'}).stripped_strings)
        phone=soup1.find('span',{'itemprop':'telephone'}).text.strip()
        name=soup1.find('span',{'itemprop':'name'}).text.strip()
        address=loc[1].strip()
        city=loc[2].strip()
        state=loc[4].strip()
        zip=loc[5].strip()
        lt=soup1.find('div',{'itemprop':'address'}).find('a')['href'].split('@')[1].split(',')
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
        store.append("rogys")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour.strip() else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
