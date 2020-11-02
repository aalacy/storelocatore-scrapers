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
    base_url = "https://www.jordans.com"
    r = session.get(base_url+'/content/about-us/store-locations')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"class":"left-sidebar-section-30"}).find_all('a')
    for atag in main:
        if atag.has_attr('href'):
            r1 = session.get(base_url+atag['href'])
            soup1=BeautifulSoup(r1.text,'lxml')
            if soup1.find('script',type="application/ld+json") != None:
                loc=json.loads(soup1.find('script',type="application/ld+json").text)
                store=[]
                store.append("https://www.jordans.com")
                store.append(loc[0]['name'])
                store.append(loc[0]['address']['streetAddress'])
                store.append(loc[0]['address']['addressLocality'])
                store.append(loc[0]['address']['addressRegion'])
                store.append(loc[0]['address']['postalCode'])
                store.append('US')  
                store.append("<MISSING>")
                store.append(loc[0]['telephone'])
                store.append("jordans")
                store.append(loc[0]['geo']['latitude'])
                store.append(loc[0]['geo']['longitude'])
                store.append(' '.join(loc[0]['openingHours']))
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
