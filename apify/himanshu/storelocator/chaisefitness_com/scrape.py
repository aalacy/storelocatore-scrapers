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
    base_url = "https://chaisefitness.com"
    r = session.get(base_url)
    soup=BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    main=soup.find('ul',{"class":"versions"}).find_all('li')
    for ltag in main:
        if ltag.find('a')['href']:
            r1 = session.get(ltag.find('a')['href'])
            soup1=BeautifulSoup(r1.text ,"lxml")
            r2 = session.get(soup1.find('a',text="Locations")['href'])
            soup2=BeautifulSoup(r2.text ,"lxml")
            atag=soup2.find('div',{"class":'page'}).find_all('a',text="More Info")
            if len(atag)>0:
                output = []
                for val in atag:
                     if val['href'] not in output:
                        output.append(val['href'])
                        r3 = session.get(val['href'])
                        soup3=BeautifulSoup(r3.text ,"lxml")
                        at=soup3.find('a',text="Get Directions")['href'].split('@')[1].split(',')
                        lat=at[0]
                        lng=at[1]
                        main=list(soup3.find('div',{"class":"perfectSquare halfShiftBlock wpb_column vc_column_container vc_col-sm-2 vc_hidden-sm vc_hidden-xs"}).stripped_strings)
                        name=main[0]
                        del main[0]
                        del main [-1]
                        phone=main[-1]
                        del main[-1]
                        ct=main[-1].split(',')
                        city=ct[0].strip()
                        state=ct[1].strip().split(' ')[0].strip()
                        zip=ct[1].strip().split(' ')[1].strip()
                        del main[-1]
                        address=' '.join(main).strip()
                        store=[]
                        store.append(base_url)
                        store.append(name)
                        store.append(address)
                        store.append(city)
                        store.append(state)
                        store.append(zip)
                        store.append("US")
                        store.append("<MISSING>")
                        store.append(phone)
                        store.append("chaisefitness")
                        store.append(lat)
                        store.append(lng)
                        store.append("<MISSING>")
                        return_main_object.append(store)
            else:
                at=soup2.find('a',text="Get Directions")['href'].split('@')[1].split(',')
                lat=at[0]
                lng=at[1]
                main=list(soup2.find('div',{"class":"perfectSquare halfShiftBlock wpb_column vc_column_container vc_col-sm-2 vc_hidden-sm vc_hidden-xs"}).stripped_strings)
                if len(main)>5:
                    del main[-1]
                name=main[0]
                del main[0]
                del main [-1]
                phone=main[-1]
                del main[-1]
                ct=main[-1].split(',')
                city=ct[0].strip()
                state=ct[1].strip().split(' ')[0].strip()
                zip=ct[1].strip().split(' ')[1].strip()
                del main[-1]
                address=' '.join(main).strip()
                store=[]
                store.append(base_url)
                store.append(name)
                store.append(address)
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append("US")
                store.append("<MISSING>")
                store.append(phone)
                store.append("chaisefitness")
                store.append(lat)
                store.append(lng)
                store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
