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
    base_url = "https://www.usaveitpharmacy.com"
    r = session.get(base_url+"/locations.html")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"id":'wsite-content'}).find('tr',{"class":"wsite-multicol-tr"}).find_all('a')
    for atag in main:
        r1 = session.get(base_url+atag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('div',{"id":'wsite-content'}).find('tr',{"class":"wsite-multicol-tr"}).find('div',{"class":"paragraph"})
        data=list(main1.stripped_strings)
        val=[]
        if len(data)==1:
            main2=soup1.find('div',{"id":'wsite-content'}).find('div',{"class":"paragraph"})
            lt = main2.find('a')['href'].split('@')[1].split(',')
            lat = lt[0].strip()
            lng = lt[1].strip()
            loc=list(main2.stripped_strings)
            address = loc[0]
            ct = loc[1].split(',')
            city = ct[0].strip()
            if "." not in loc[2]:
                del loc[2]
            phone = loc[2].replace('\u200b', '').strip()
            state = ct[1].strip().split(' ')[0].strip()
            zip = ct[1].strip().split(' ')[1].strip()
            del loc[0]
            del loc[0]
            del loc[0]
            hour = ' '.join(loc)
            store = []
            store.append(base_url)
            store.append("U-Save-It Pharmacy")
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("usaveitpharmacy")
            store.append(lat)
            store.append(lng)
            store.append(hour)
            return_main_object.append(store)
        elif len(data)>4:
            lt=main1.find('a')['href'].split('@')[1].split(',')
            lat=lt[0].strip()
            lng=lt[1].strip()
            for item in data:
                if "Product" in item:
                    break
                if item!="\u200b":
                    val.append(item.replace("\u200b",''))
            address=val[0]
            ct=val[1].split(',')
            city=ct[0].strip()
            phone=val[2].replace('\u200b','').strip()
            state=ct[1].strip().split(' ')[0].strip()
            zip=ct[1].strip().split(' ')[1].strip()
            del val[0]
            del val[0]
            del val[0]
            hour=' '.join(val)
            store=[]
            store.append(base_url)
            store.append("U-Save-It Pharmacy")
            store.append(address)
            store.append(city)
            store.append(state)
            store.append(zip)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("usaveitpharmacy")
            store.append(lat)
            store.append(lng)
            store.append(hour)
            return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
