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
    base_url ="https://www.rockler.com"
    return_main_object=[]
    r = session.get(base_url+'/retail/stores')
    soup=BeautifulSoup(r.text,'lxml')
    output=[]
    main=soup.find('ul',{"class":'cms-menu'}).find('ul').find('ul').find_all('a')
    for dt in main:
        r1 = session.get(dt['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('ul',{"class":'cms-menu'}).find('ul').find('ul').find_all('a')
        for dt1 in main1:
            r2 = session.get(dt1['href'])
            soup2 = BeautifulSoup(r2.text, 'lxml')
            if soup2.find('h3', text="Store Hours")!=None:
                main2 = soup2.find('h3', text="Store Hours").parent.parent
                loc=list(main2.stripped_strings)
                hour=loc[-6]+' '+loc[-5]+' '+loc[-4]+' '+loc[-3]+' '+loc[-2]+' '+loc[-1]
                name=loc[0].strip()
                i=loc.index('Phone:')
                print(loc)
                print(i)
                if i>3:
                    del loc[1]
                # if len(loc)>14:
                #     address=loc[2].strip()
                #     del loc[1]
                address=loc[1].strip()
                addr=loc[1].split(',')
                if len(addr)==2 and i==2:
                    state=addr[-1].strip().split(' ')[0]
                    zip=addr[-1].strip().split(' ')[1]
                    adr=addr[0].strip().split(' ')
                    city=adr[-1].strip()
                    del adr[-1]
                    address=' '.join(adr)
                    phone = loc[3].strip()
                else:
                    ct=loc[2].split(',')
                    city=ct[0].strip()
                    state=ct[1].strip().split(' ')[0].strip()
                    zip=ct[1].strip().split(' ')[1].strip()
                    phone=loc[4].strip()
                storeno=''
                lat=soup2.find('h3', text="Store Hours").parent.parent.parent.find('iframe')['src'].split('!3d')[1].split('!')[0].strip()
                lng=soup2.find('h3', text="Store Hours").parent.parent.parent.find('iframe')['src'].split('!2d')[1].split('!')[0].strip()
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
                store.append("rockler")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hour if hour.strip() else "<MISSING>")
                ads=address+' '+city+' '+state+' '+zip
                if ads not in output:
                    output.append(ads)
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
