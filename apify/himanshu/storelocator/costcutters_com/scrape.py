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
    base_url = "https://www.signaturestyle.com"
    r = requests.get(base_url+"/salon-directory.html")
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find('div',{"class":"content parsys"}).find_all('a')
    for atag in main:
        r1 = requests.get(base_url+atag['href'])
        soup1=BeautifulSoup(r1.text,'lxml')
        if soup1.find('div',{"class":"each-state"}) != None:
            main1=soup1.find_all('div',{"class":"salon-group"})
            for atag1 in main1:
                r2 = requests.get(base_url+atag1.find('a')['href'])
                soup2=BeautifulSoup(r2.text,'lxml')
                storeno=soup2.find('input',{"id":"nearBySdpSalonId"})['value']
                name=soup2.find('h2',{"class":"salontitle_salonlrgtxt"}).text.strip()
                phone=soup2.find('span',{"itemprop":"telephone"}).text.strip()
                address=soup2.find('span',{"itemprop":"streetAddress"}).text.strip()
                city=soup2.find('span',{"itemprop":"addressLocality"}).text.strip()
                state=soup2.find('span',{"itemprop":"addressRegion"}).text.strip()
                zip=soup2.find('span',{"itemprop":"postalCode"}).text.strip()
                lat=soup2.find('meta',{"itemprop":"latitude"})['content'].strip()
                lng=soup2.find('meta',{"itemprop":"longitude"})['content'].strip()
                allhr=soup2.find_all('meta',itemprop="openingHours")
                if len(zip)==5:
                    country_code="US"
                else:
                    country_code="CA"
                hour=""
                for hr in allhr:
                    hour+=hr['content']+" "
                store=[]
                store.append(base_url)
                store.append(name)
                store.append(address)
                store.append(city)
                store.append(state)
                store.append(zip)
                store.append(country_code)
                store.append(storeno)
                store.append(phone)
                store.append("Cost Cutters")
                store.append(lat)
                store.append(lng)
                if hour:
                    store.append(hour.strip())
                else:
                    store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
