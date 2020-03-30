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
    base_url = "https://www.camper.com"
    r = session.get(base_url+"/en_US/shops")
    soup=BeautifulSoup(r.text ,"lxml")
    return_main_object = []
    main=soup.find_all('script')
    for script in main:
        if "var ciudades" in script.text:
            data=eval(script.text.split('var ciudades = ')[1].split(';')[0])
            if "USA" in data:
                r1 = session.get(base_url+"/en_US/shops/usa")
                soup1=BeautifulSoup(r1.text ,"lxml")
                main1=soup1.find('div',{"id":"lista"}).find_all('div',{"class":"store_item"})
                for atag in main1:
                    link=atag.find('a',{'class':"btn_view_store"})['href']
                    storeno=link.split('-')[-1]
                    r2 = session.get(base_url+link)
                    soup2=BeautifulSoup(r2.text ,"lxml")
                    name=soup2.find('h2',{"itemprop":"name"}).text.strip()
                    address=soup2.find('span',{"itemprop":"streetAddress"}).text.strip()
                    zip=soup2.find('span',{"itemprop":"postalCode"}).text.strip()
                    city=soup2.find('span',{"itemprop":"addressLocality"}).text.strip()
                    phone=soup2.find('span',{"itemprop":"telephone"}).text.strip()
                    hour="<MISSING>"
                    if soup2.find('div',{"class":"hours"}) != None:
                        hour=""
                        for hr in soup2.find_all('li',{"itemprop":"openingHours"}):
                            hour+=hr['content']+" "
                    store=[]
                    store.append(base_url)
                    store.append(name)
                    store.append(address)
                    store.append(city)
                    store.append("<MISSING>")
                    store.append(zip)
                    store.append("US")
                    store.append(storeno)
                    store.append(phone)
                    store.append("camper")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(hour)
                    return_main_object.append(store)
            if "CANADA" in data:
                r1 = session.get(base_url+"/en_US/shops/canada")
                soup1=BeautifulSoup(r1.text ,"lxml")
                main1=soup1.find('div',{"id":"lista"}).find_all('div',{"class":"store_item"})
                for atag in main1:
                    link=atag.find('a',{'class':"btn_view_store"})['href']
                    storeno=link.split('-')[-1]
                    r2 = session.get(base_url+link)
                    soup2=BeautifulSoup(r2.text ,"lxml")
                    name=soup2.find('h2',{"itemprop":"name"}).text.strip()
                    address=soup2.find('span',{"itemprop":"streetAddress"}).text.strip()
                    zip=soup2.find('span',{"itemprop":"postalCode"}).text.strip()
                    city=soup2.find('span',{"itemprop":"addressLocality"}).text.strip()
                    phone=soup2.find('span',{"itemprop":"telephone"}).text.strip()
                    hour="<MISSING>"
                    if soup2.find('div',{"class":"hours"}) != None:
                        hour=""
                        for hr in soup2.find_all('li',{"itemprop":"openingHours"}):
                            hour+=hr['content']+" "
                    store=[]
                    store.append(base_url)
                    store.append(name)
                    store.append(address)
                    store.append(city)
                    store.append("<MISSING>")
                    store.append(zip)
                    store.append("CA")
                    store.append(storeno)
                    store.append(phone)
                    store.append("camper")
                    store.append("<MISSING>")
                    store.append("<MISSING>")
                    store.append(hour)
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
