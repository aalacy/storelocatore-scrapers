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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="https://www.breguet.com"
    return_main_object=[]
    output=[]
    r = session.get("https://store.breguet.com/en/point-of-sale?country=2277&region=All")
    soup=BeautifulSoup(r.text,'lxml')
    main=json.loads(soup.find('script',text=re.compile('jQuery.extend')).text.split('"markers":')[1].split('],')[0]+']')
    for atag in main:
        lat=atag['latitude']
        lng=atag['longitude']
        soup1=BeautifulSoup(atag['text'],'lxml')
        r1=session.get("https://store.breguet.com"+soup1.find('a')['href'])
        soup2=BeautifulSoup(r1.text,'lxml')
        name=soup2.find('h1',{"class":'title'}).text.strip()
        addr=list(soup2.find('div',{'class':"item-address"}).stripped_strings)
        address=addr[1].strip()
        if len(addr)==4:
            address+=' '+addr[2].strip()
        ct=addr[-1].split(' ')
        state=''
        if len(ct)>4:
            ct1=addr[-1].split('  ')
            address=ct1[0].strip()
            ct2=ct1[-1].split(' ')
            if re.match('^[0-9]*$',ct2[0]):
                zip=ct2[0].strip()
                del ct2[0]
                city=' '.join(ct2)
            else:
                state=ct2[0].strip()
                zip=ct2[1].strip()
                del ct2[0]
                del ct2[0]
                city=' '.join(ct2)
        else:
            if re.match('^[0-9]*$',ct[0]):
                zip=ct[0].strip()
                del ct[0]
                city=' '.join(ct)
            else:
                state=ct[0].strip()
                zip=ct[1].strip()
                del ct[0]
                del ct[0]
                city=' '.join(ct)
        country="US"
        storeno=''
        phone=soup2.find('div',{"class":"tel"}).text.replace("Tel:",'').strip()
        hour=''
        if soup2.find('div',{'class':"item-time"})!=None:
            hour=' '.join(list(soup2.find('div',{'class':"item-time"}).find('ul').stripped_strings))
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
        store.append("<MISSING>")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour.strip() else "<MISSING>")
        store.append("<MISSING>")
        adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
        if adrr not in output:
            output.append(adrr)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
