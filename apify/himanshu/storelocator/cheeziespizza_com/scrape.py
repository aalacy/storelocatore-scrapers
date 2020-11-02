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
    base_url = "http://www.cheeziespizza.com"
    r = session.get("http://www.cheeziespizza.com/locations-results?gmw_post=locations&gmw_address%5B0%5D&gmw_distance=200&gmw_units=imperial&gmw_form=1&gmw_per_page=1000000000&gmw_lat&gmw_lng&gmw_px=pt&action=gmw_post")
    soup=BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    main=soup.find('div',{"id":"wppl-results-wrapper-"}).find_all('div',{"class":"wppl-single-result"})
    for detail in main:
        name=detail.find('a').text.replace('+','').strip()
        storeno=name.split('(')[-1].split(')')[0].strip()
        phone=detail.find('div',{"class":"gmw-phone"}).text.replace('Phone:','').strip()
        main_address=list(detail.find('div',{"class":"wppl-address"}).text.strip().split(','))
        if len(main_address)==1:
            loc=main_address[0].split(' ')
            country=loc[-1]
            del loc[-1]
            zip=loc[-1]
            del loc[-1]
            state=loc[-1]
            del loc[-1]
            city=loc[-1]
            del loc[-1]
            address=' '.join(loc)
        else:
            address=main_address[0]
            city=main_address[1]
            state=main_address[2].strip().split(' ')[0].strip()
            zip=main_address[2].strip().split(' ')[1].strip()
            country=main_address[3]
        if country.strip()=="USA":
            country="US"
        link=detail.find('a')['href']
        r1 = session.get(link)
        soup1=BeautifulSoup(r1.text ,"lxml")
        hour=list(soup1.find('div',{"id":"content"}).find('div',{"class":'hours'}).stripped_strings)
        del hour[0]
        hour=' '.join(hour)
        store=[]
        store.append(base_url)
        store.append(name.strip())
        store.append(address.strip())
        store.append(city.strip())
        store.append(state.strip())
        store.append(zip.strip())
        store.append(country.strip())
        store.append(storeno.strip())
        store.append(phone.strip())
        store.append("cheeziespizza")
        store.append("<MISSING>")
        store.append("<MISSING>")
        store.append(hour.strip())
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
