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
    base_url = "https://www.peanutgallerychildcare.com"
    headers={"user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"}
    r = session.get(base_url,headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('li',{"class":"menu-find-your-school"}).find('ul').find_all('li')
    for li in main:
        r1 = session.get(li.find('a')['href'],headers=headers)
        soup1=BeautifulSoup(r1.text,'lxml')
        sz=list(soup1.find('div',{"itemprop":"address"}).stripped_strings)
        if ',' in sz:
            i=sz.index(',')
            del sz[i]
        address=sz[1].strip()
        city=sz[2].strip()
        state=sz[3].strip()
        zip=sz[4].strip()
        lt=soup1.find('div',{"itemprop":"address"}).find('a')['href'].split('@')[1].split(',')
        lat=lt[0].strip()
        lng=lt[1].strip()
        name=soup1.find('span',itemprop="name").text.strip()
        phone=soup1.find('span',itemprop="telephone").text.strip()
        country="US"
        al=soup1.find('div',{"class":"school-details"}).find_all('div',{"class":"col-xs-12"})
        hour=' '.join(list(al[3].stripped_strings))
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
        store.append("peanutgallerychildcare")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
