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
    base_url = "https://robinsonstkd.com"
    return_main_object=[]
    r = session.get(base_url)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('li',{'class':'about-school-menu'}).find_all('a',href=re.compile("^school/"))
    for dt in main:
        r1 = session.get(base_url+'/'+dt['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('div',{'class':'school-address'})
        storeno=''
        loc=main1.find('span',{'class':"address"}).text.strip('\t')
        loc=re.sub(r'\s+',' ',loc).strip().split(',')
        city=loc[-2].strip()
        state=loc[-1].strip().split(' ')[0].strip()
        zip=loc[-1].strip().split(' ')[1].strip()
        del loc[-1]
        del loc[-1]
        address=' '.join(loc).strip()
        country='US'
        lat=''
        lng=''
        name=main1.find('h2').text.strip()
        phone=main1.find('span',{'class':"no"}).text.strip()
        hour=''
        hour=' '.join(main1.find('ul',{'class':"working-hours"}).stripped_strings)
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
        store.append("robinsonstkd")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour.strip() else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
