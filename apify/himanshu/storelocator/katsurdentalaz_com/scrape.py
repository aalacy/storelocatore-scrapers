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
    base_url = "https://www.katsurdentalaz.com/map/#all"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3"}

    r = session.get(base_url,headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"class":"office-list"}).find('ul',{"class":"list"}).find_all('li')
    for atag in main:
        lat=atag['data-lat']
        lng=atag['data-lng']
        r1 = session.get(atag.find('a')['href'],headers=headers)
        soup1=BeautifulSoup(r1.text,'lxml')
        loc=list(soup1.find('div',{"id":"office-info-mobile"}).stripped_strings)
        phone=soup1.find('article',{'id':'content'})['data-phone']
        storeno=soup1.find('article',{'id':'content'})['data-id']
        name=soup1.find('article',{'id':'content'})['data-name']
        hour=list(soup1.find('div',{"class":"hours"}).stripped_strings)
        del hour[0]
        address=loc[1].strip()
        city=loc[2].strip()
        state=loc[4].strip()
        zip=loc[5].strip()
        store=[]
        store.append("https://www.katsurdentalaz.com")
        store.append(name)
        store.append(address)
        store.append(city)
        store.append(state)
        store.append(zip)
        store.append('US')  
        store.append(storeno)
        store.append(phone)
        store.append("katsurdentalaz")
        store.append(lat)
        store.append(lng)
        store.append(' '.join(hour))
        return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
