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
    base_url = "https://www.rocsstores.com"
    r = session.get(base_url+'/locations/')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"id":"et-boc"}).find('div',{"class":'et_pb_row et_pb_row_1'}).find('table').find_all('tr')
    del main[0]
    for atag in main:
        ct=list(atag.stripped_strings)
        city=ct[0].strip()
        d=ct[1].strip().split(' ')
        phone=d[-1].strip()
        del d[-1]
        address=' '.join(d).strip()
        name="<MISSING>"
        state="<MISSING>"
        zip="<MISSING>"
        country="<MISSING>"
        lat="<MISSING>"
        lng="<MISSING>"
        storeno="<MISSING>"
        nm=atag.find('a')['href'].split('name=')
        if len(nm)==2:
            name=nm[1].split('&')[0].replace('+',' ').strip()
        st=atag.find('a')['href'].split('state=')
        if len(st)==2:
            state=st[1].split('&')[0].strip()
        zp=atag.find('a')['href'].split('zipcode=')
        if len(zp)==2:
            zip=zp[1].split('&')[0].strip()
        cnt=atag.find('a')['href'].split('country=')
        if len(cnt)==2:
            country=cnt[1].split('&')[0].strip()
        lt=atag.find('a')['href'].split('latitude=')
        if len(lt)==2:
            lat=lt[1].split('&')[0].strip()
        lg=atag.find('a')['href'].split('longitude=')
        if len(lg)==2:
            lng=lg[1].split('&')[0].strip()
        no=atag.find('a')['href'].split('id=')
        if len(no)==2:
            storeno=no[1].split('#')[0].strip()
        store=[]
        store.append(base_url)
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append(country)
        store.append(storeno)
        store.append(phone)
        store.append("rocsstores")
        store.append(lat)
        store.append(lng)
        store.append("<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
