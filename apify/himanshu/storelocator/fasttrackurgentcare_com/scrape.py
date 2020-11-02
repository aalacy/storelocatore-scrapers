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
    base_url = "https://www.fasttrackurgentcare.com/locations-and-hours/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main = soup.find('div',{"id":"accordionExample"}).find_all('div',{"class":"card"})
    for location in main:
        lat=location.find('button')['data-lat']
        lng=location.find('button')['data-lng']
        name=location.find('button')['data-title']
        address=location.find('button')['data-address']
        st=location.find('button')['data-citystzip'].split(' ')
        zip=st[-1]
        del st[-1]
        state=st[-1]
        del st[-1]
        city=' '.join(st).strip()
        dt=list(location.find('div',{"class":"card-content"}).stripped_strings)
        store=[]
        store.append("hhttps://www.fasttrackurgentcare.com")
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append('US')
        store.append("<MISSING>")
        store.append(dt[3])
        store.append("fasttrackurgentcare")
        store.append(lat)
        store.append(lng)
        store.append(dt[4])
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
