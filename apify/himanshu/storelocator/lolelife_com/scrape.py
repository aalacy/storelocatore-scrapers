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
    base_url = "https://www.lolelife.com"
    r = session.get(base_url+"/pages/storelocator")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    output=[]
    main=soup.find('div',{"class":'filter_locator'}).find_all('a')
    for atag in main:
        r1 = session.get(base_url+"/apps/proxy/getStores?country="+atag['href'].split('/')[-1].strip().upper()).json()
        for location in r1:
            store=[]
            hour=re.sub(r'"+', '',location['weekday'].replace('[','').replace(']',''))
            store.append(base_url)
            store.append(location['title'].replace("\x90",' ').replace("\u011b",' ').strip())
            store.append(location['address'].replace("\x90",' ').replace("\u011b",' ').strip())
            store.append(location['city'].replace("\x90",' ').replace("\u011b",' ').strip())
            if location['state']:
                store.append(location['state'].replace("\x90",' ').replace("\u011b",' ').strip())
            else:
                store.append("<MISSING>")
            if location['postalcode']:
                zp=location['postalcode']
                if len(location['postalcode'])==4:
                    zp="0"+location['postalcode'].replace("\x90",' ').replace("\u011b",' ').strip()
                store.append(zp)
            else:
                store.append("<MISSING>")
            if location['country']:
                store.append(location['country'].replace("\x90",' ').replace("\u011b",' ').strip())
            else:
                store.append("<MISSING>")
            if location['store_id']:
                store.append(location['store_id'].replace("\x90",' ').replace("\u011b",' '))
            else:
                store.append("<MISSING>")
            if location['phone']:
                if len(location['phone'])>4:
                    store.append(location['phone'].replace("\x90",' ').replace("\u011b",' '))
                else:
                    store.append("<MISSING>")
            else:
                store.append("<MISSING>")
            store.append("lolelife")
            if location['latitude']:
                store.append(location['latitude'].replace("\x90",' ').replace("\u011b",' '))
            else:
                store.append("<MISSING>")
            if location['longitude']:
                store.append(location['longitude'].replace("\x90",' ').replace("\u011b",' '))
            else:
                store.append("<MISSING>")
            if hour:
                store.append(hour.replace("\x90",' ').replace("\u011b",' '))
            else:
                store.append("<MISSING>")
            adrr =location['address'].strip() + ' ' + location['city'].strip()
            if adrr not in output:
                output.append(adrr)
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
