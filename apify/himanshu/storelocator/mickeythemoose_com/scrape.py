import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://mickeythemoose.com"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36',
        "Content-Type":'application/x-www-form-urlencoded; charset=UTF-8'
    }
    r = requests.post("https://mickeythemoose.com/wp-json/wpgmza/v1/marker-listing/",data='phpClass=WPGMZA%5CMarkerListing%5CBasicTable&start=0&length=10000&map_id=1',headers=headers).json()
    return_main_object = []
    for loc in r['meta']:
        r1=requests.get(loc['link'])
        name=loc['title'].strip()
        storeno=loc['id']
        lat=loc['lat']
        lng=loc['lng']
        soup=BeautifulSoup(r1.text,'lxml')
        main=list(soup.find('div',{"class":"store_info"}).find('div',{"class":"gray-box"}).stripped_strings)
        del main[0]
        address=main[0].strip()
        ct=main[1].split(',')
        city=ct[0].strip()
        state=ct[1].strip().split(' ')[0].strip()
        zip=ct[1].strip().split(' ')[1].strip()
        phone=main[2].strip()
        del main[0]
        del main[0]
        del main[0]
        del main[0]
        del main[0]
        hour=' '.join(main).replace('–>','').strip()
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
        store.append("mickeythemoose")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
