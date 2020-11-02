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
    base_url = "https://www.cnb.com/"
    r = session.get("https://locations.cnb.com/")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    output=[]
    main=soup.find('div',{"id":'mapList'}).find_all('a',{"class":'ga-link'})
    for atag in main:
        r1 = session.get(atag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('div',{"id":'mapList'}).find_all('a',{"class":'ga-link'})
        for atag1 in main1:
            r2 = session.get(atag1['href'])
            soup2=BeautifulSoup(r2.text,'lxml')
            main2=soup2.find_all('div',{"class":'locationName'})
            for atag2 in main2:
                r3 = session.get(atag2.find('a')['href'])
                soup3=BeautifulSoup(r3.text,'lxml')
                loc=json.loads(soup3.find('script',{"type":"application/ld+json"}).text, strict=False)
                name=loc[0]['name'].replace('The City National Difference - ','').strip()
                lat=loc[0]['geo']['latitude']
                lng=loc[0]['geo']['longitude']
                hour=loc[0]['openingHours']
                address=loc[0]['address']['streetAddress']
                city=loc[0]['address']['addressLocality']
                state=loc[0]['address']['addressRegion']
                zip=loc[0]['address']['postalCode']
                phone=loc[0]['address']['telephone']
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
                store.append("cnb")
                store.append(lat)
                store.append(lng)
                if hour:
                    store.append(hour)
                else:
                    store.append("<MISSING>")
                if zip not in output:
                    output.append(zip)
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
