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
    base_url = "https://www.kilwins.com"
    r = session.get(base_url+"/stores/all")
    soup=BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    main=soup.find('div',{"id":"block-views-stores-by-state-block-1"}).find_all('div',{"class":"views-field views-field-title"})
    for atag in main:
        r1 = session.get(base_url+atag.find('a')['href'])
        soup1=BeautifulSoup(r1.text ,"lxml")
        location=json.loads(soup1.find("script",{"type":"application/ld+json"}).text,strict=False)
        if soup1.find('span',{"class":"oh-display-grouped"}) == None:
            hour="<MISSING>"
        else:
            hour=' '.join(list(soup1.find('span',{"class":"oh-display-grouped"}).stripped_strings))
        store = []
        store.append(base_url)
        store.append(location['name'])
        store.append(location['address']['streetAddress'])
        store.append(location['address']['addressLocality'])
        store.append(location['address']['addressRegion'])
        store.append(location['address']['postalCode'])
        store.append(location['address']['addressCountry'])
        store.append("<MISSING>")
        try:
            store.append(location['telephone'])
        except:
            store.append("<MISSING>")
        store.append("Kilwins")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hour)
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
