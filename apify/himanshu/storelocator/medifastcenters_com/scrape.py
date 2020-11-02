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
    base_url = "http://medifastcenters.com"
    r = session.get(base_url+'/findaCenter/')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    output=[]
    main=soup.find('select',{'id':"ddlStates"}).find_all('option')
    del main[0]
    for opt in main:
        r1 = session.get(base_url+'/findaCenter/results.aspx?state='+opt['value'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find_all('div',{"class":"block_services_type_1"})
        scr=''
        for script in soup1.find_all('script',{"type":"text/javascript"}):
            if "var map" in script.text:
                scr=script.text
        c=0
        for dt in main1:
            lt=scr.split('var marker'+str(c))[1].split('LatLng(')[1].split(')')[0].split(',')
            lat=lt[0].strip()
            lng=lt[1].strip()
            c=c+1
            loc=list(dt.find('div',{"class":"service"}).stripped_strings)
            del loc[-1]
            phone=loc[-1].replace('Phone:','').strip()
            del loc[-1]
            del loc[-1]
            ct=loc[-1].split(',')
            city=ct[0].strip()
            state=ct[1].strip().split(' ')[0].strip()
            zip=ct[1].strip().split(' ')[1].strip()
            name=loc[0].strip()
            del loc[-1]
            del loc[0]
            del loc[0]
            address=' '.join(loc).strip()
            hour=list(dt.find('div',{"class":"service2"}).stripped_strings)
            del hour[0]
            country='US'
            hour=' '.join(hour).strip()
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
            store.append("medifastcenters")
            store.append(lat if lat else "<MISSING>")
            store.append(lng if lng else "<MISSING>")
            store.append(hour if hour else "<MISSING>")
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
