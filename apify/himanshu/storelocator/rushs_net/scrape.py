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
    base_url = "http://www.rushs.net"
    r = session.get(base_url+"/locations")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"id":'locations'}).find_all('div',{"class":"location"})
    for loc in main:
        name=loc.find('h3').text.strip().split('–')[0].strip()
        md=list(loc.find('div',{"class":"address"}).stripped_strings)
        address=md[1].strip()
        phone=md[-1]
        city=md[2].split(',')[0].strip()
        state=md[2].split(',')[1].strip().split(' ')[0].strip()
        zip=md[2].split(',')[1].strip().split(' ')[1].strip()
        lt=loc.find('iframe')['src'].split('&ll=')[1].split('&')[0].split(',')
        lat=lt[0]
        lng=lt[1]
        hr=list(loc.find('div',{"class":'hours'}).stripped_strings)
        hour=hr[2]+" : "+hr[1].replace('\xa0','')
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
        store.append("rushs")
        store.append(lat)
        store.append(lng)
        store.append(hour)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()