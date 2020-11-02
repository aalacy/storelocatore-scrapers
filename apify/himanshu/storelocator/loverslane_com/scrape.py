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
    base_url = "https://www.loverslane.com"
    r = session.get(base_url+'/stores')
    soup=BeautifulSoup(r.text,'lxml')
    return_main_object = []
    main=soup.find_all('script', type="text/javascript")
    for script in main:
        if "var stores" in script.text:
            for link in eval(script.text.split('var stores =')[1].split('];')[0]+"]"):
                lat=link[1]
                lng=link[2]
                name=link[0]
                r1 = session.get(base_url+link[-1])
                soup1=BeautifulSoup(r1.text,'lxml')
                address=soup1.find('span',itemprop="streetAddress").text.strip()
                city=soup1.find('span',itemprop="addressLocality").text.strip()
                state=soup1.find('span',itemprop="addressRegion").text.strip()
                zip=soup1.find('span',itemprop="postalCode").text.strip()
                phone=soup1.find('span',itemprop="telephone").text.strip()
                hour=""
                for hr in soup1.find_all('span',itemprop="openingHours"):
                    hour+=hr.text+" , "
                hour=hour.rstrip(' , ')
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
                store.append("loverslane")
                store.append(lat)
                store.append(lng)
                if hour:
                    store.append(hour)
                else:
                    store.append("<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
