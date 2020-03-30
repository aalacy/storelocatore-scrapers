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
    base_url ="https://snuffers.com"
    return_main_object=[]
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = session.get(base_url+'/locations/', headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find_all('div',{"class":'location-info'})
    for dt in main:
        loc = list(dt.stripped_strings)
        del loc[0]
        del loc[0]
        del loc[0]
        hour = ' '.join(loc)

        r = session.get(dt.find('a',{'class':'more-btn'})['href']+'?req=more-info', headers=headers)
        soup = BeautifulSoup(r.text, 'lxml')
        vk = soup.find('div',{'class':'location-info'})

        name= vk.find('h3').text.strip()
        address = vk.find('span',{'itemprop':'streetAddress'}).text.strip()
        city = ''

        if vk.find('span',{'itemprop':'addressLocality'}) != None:
            city = vk.find('span',{'itemprop':'addressLocality'}).text.strip().split(',')[0].strip()
        state = ''
        if vk.find('span', {'itemprop': 'addressRegion'}) != None:
            state = vk.find('span',{'itemprop':'addressRegion'}).text.strip()
        zip = ''
        if vk.find('span', {'itemprop': 'postalCode'}) != None:
            zip = vk.find('span', {'itemprop': 'postalCode'}).text.strip()
        phone  = vk.find('div',{'class':'phone'}).text.strip().replace('P: ','')

        lat =''
        lng = ''
        storeno = ''
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
        store.append("<MISSING>")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour.strip() else "<MISSING>")
        store.append(dt.find('a',{'class':'more-btn'})['href']+'?req=more-info')
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
