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
    base_url ="https://www.pointstire.com"
    return_main_object=[]
    url=[]
    output=[]
    r = session.get(base_url+'/home.aspx')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find('div',{"id":'accordion'}).find_all('a',{'href':re.compile("/")})
    for atag in main:
        if "https://www" in atag['href']:
            url.append(atag['href'])
        else:
            if "/locations/" not in atag['href']:
                url.append(base_url+atag['href'])
            else:
                r1 = session.get(base_url+atag['href'])
                soup1=BeautifulSoup(r1.text,'lxml') 
                main1=soup1.find('span',{"id":'MainContent_locationDetails2'}).find('table').find_all('a',text=re.compile('Make this My Store'))
                for tg in main1:
                    if "https://www" in tg['href']:
                        url.append(tg['href'])  
                    else:
                        url.append(base_url+tg['href'])  
    for page_url in url:
        try:
            r1 = session.get(page_url)
            soup1=BeautifulSoup(r1.text,'lxml')
            main1=list(soup1.find('div',{"class":'storeInfoDetails'}).stripped_strings)
            lt=soup1.find('div',{"class":'storeInfoMap'}).find('img')['src'].split("center=")[1].split('&')[0].split(',')
            lat=lt[0]
            lng=lt[1]
            del main1[0]
            name=main1[0].strip()
            address=main1[1].strip()
            ct=main1[2].split(',')
            city=ct[0].strip()
            state=ct[1].strip().split(' ')[0].strip()
            zip=ct[1].strip().split(' ')[1].strip()
            country="US"
            storeno=''
            phone=main1[3].strip()
            hour=main1[8]+' '+main1[9]+' '+main1[10]
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
            store.append(page_url if page_url else "<MISSING>")
            adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + zip
            if adrr not in output:
                output.append(adrr)
                yield store
        except:
            continue

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
