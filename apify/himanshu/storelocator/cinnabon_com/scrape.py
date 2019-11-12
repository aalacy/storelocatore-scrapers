import csv
import requests
from bs4 import BeautifulSoup
import re
import json

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.cinnabon.com"
    r = requests.get(base_url+'/locations')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    ouptut=[]
    main=soup.find('div',{"class":"national-list"}).find_all("a")
    for link in main:
        r1 = requests.get(base_url+link['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        main1=soup1.find('div',{"class":"state-national-list"}).find_all("a")
        for link1 in main1:
            r2 = requests.get(base_url+link1['href'])
            soup2=BeautifulSoup(r2.text,'lxml')
            if soup2.find('div',{"class":"city-list"})!=None:
                main2=soup2.find('div',{"class":"city-list"}).find_all("li")
                for ltag in main2:
                    loc=list(ltag.stripped_strings)
                    # print(loc)
                    name=loc[0].strip()
                    address=loc[1].strip()
                    ct=loc[2].split(',')
                    city=ct[0].strip()
                    state=ct[1].strip().split(' ')[0].strip()
                    zip=ct[1].strip().split(' ')[1].strip()
                    if len(loc)>3:
                        phone=loc[3].strip()
                    else:
                        phone="<MISSING>"
                    r3 = requests.get(base_url+ltag.find('a')['href'])
                    soup3=BeautifulSoup(r3.text,'lxml')
                    hour="<MISSING>"
                    if soup3.find('div',{"class":"hours-wrapper"})!=None:
                        hour=' '.join(list(soup3.find('div',{"class":"hours-wrapper"}).stripped_strings))
                        print(hour)
                    if soup3.find('div',{"class":"address-wrapper"})!=None:
                        lt=soup3.find('div',{"class":"address-wrapper"}).find('a',text="see map")['href']
                        lat=lt.split('AddressLatitude=')[1].split('&')[0].strip()
                        lng=lt.split('AddressLongitude=')[1].split('&')[0].strip()
                    else:
                        lat="<MISSING>"
                        lng="<MISSING>"
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
                    store.append("cinnabon")
                    store.append(lat)
                    store.append(lng)
                    store.append(hour)
                    if zip not in ouptut:
                       ouptut.append(zip)
                       return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
