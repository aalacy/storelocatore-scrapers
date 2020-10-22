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
    base_url = "https://wahlburgers.com"
    r = session.get(base_url+"/all-locations")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('section',{"id":'body'}).find('div',{"class":"locations"}).find('div',{"class":"cell"}).find_all('a')
    for atag in main:
        country=atag['href'].split('/')[-1]
        if country=="canada":
            country="CA"
        elif country == "uk":
            country="UK"
        else:
            country="US"
        if base_url+atag['href']=="https://wahlburgers.com/all-locations/connecticut":
            continue
        r1 = session.get(base_url+atag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('section',{"id":'body'}).find('div',{"class":"locationset"}).find('div',{"class":"cell"}).find_all('a',{"class":'fadey'})
        for atag1 in main1:
            r2 = session.get(base_url+atag1['href'])
            soup2=BeautifulSoup(r2.text,'html5lib')
            if soup2.find('script',{"type":'application/ld+json'}) != None:
                loc=json.loads(soup2.find('script',{"type":'application/ld+json'}).text,strict=False)
                store=[]
                hour=' '.join(loc['openingHours'])
                lt=soup2.find('div',{"class":'responsive-embed widescreen'}).find('iframe')['src']
                lng=lt.split('!2d')[1].split('!3d')[0]
                lat=lt.split('!3d')[1].split('!')[0]
                if len(soup2.find('div',{"class":'insideThing'}).find_all('div'))>4:
                    zip=list(soup2.find('div',{"class":'insideThing'}).find_all('div')[2].stripped_strings)[-1].split('\n')[-1].strip()
                else:
                    zip=list(soup2.find('div',{"class":'insideThing'}).find_all('div')[1].stripped_strings)[-1].split('\n')[-1].strip()
                if len(zip)!=5:
                    zip=list(soup2.find('div',{"class":'insideThing'}).find_all('div')[2].stripped_strings)[-1].split('\n')[-1].strip()
                if zip == "Sun-Mon: 5am-10pm subject to departing flight schedules":
                    zip = "L5P 1B2"
                store.append(base_url)
                store.append(loc['name'].strip().lstrip().rstrip().replace("\n","").replace("\t","").replace("\n "," "))
                store.append(loc['address']['streetAddress'].strip())
                store.append(loc['address']['addressLocality'].strip())
                store.append(loc['address']['addressRegion'].strip())
                store.append(zip)
                store.append(country)
                store.append("<MISSING>")
                if loc['telephone']:
                    store.append(loc['telephone'])
                else:
                    store.append("<MISSING>")
                store.append("<MISSING>")
                store.append(lat)
                store.append(lng)
                if hour:
                    store.append(hour)
                else:
                    store.append("<MISSING>")
                store.append(base_url+atag1['href'])
                if "66877" in zip:
                    continue
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()

