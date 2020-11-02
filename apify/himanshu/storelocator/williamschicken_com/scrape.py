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
    base_url = "http://www.williamschicken.com"
    return_main_object=[]
    r = session.get(base_url+'/willchickwp/wp-content/plugins/superstorefinder-wp/ssf-wp-xml.php?t=1564665902910')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find_all('item')
    for atag in main:
        madd=atag.find('address').text.split(',')
        name=atag.find('location').text.strip()
        address=madd[0].strip()
        state=madd[1].strip().split(' ')[0].strip()
        zip=madd[1].strip().split(' ')[1].strip()
        phone=atag.find('telephone').text.strip()
        lat=atag.find('latitude').text.strip()
        lng=atag.find('longitude').text.strip()
        country="US"
        storeno=''
        hour=''
        store=[]
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append("<INACCESSIBLE>")
        store.append(state if state else "<MISSING>")
        store.append(zip if zip else "<MISSING>")
        store.append(country if country else "<MISSING>")
        store.append(storeno if storeno else "<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append("youngsenvironmental")
        store.append(lat if lat else "<MISSING>")
        store.append(lng if lng else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
