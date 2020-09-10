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
    addressess = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "http://thegrandtheatre.com"
   
    r = session.get("https://thegrandtheatre.com/locations",headers=headers)
    soup=BeautifulSoup(r.text,'lxml')
    main = soup.find("div",{"class":"container clearfix"}).find_all('div',{"class":"slide locationblock"})
    for sub in main:
        link = sub.find("a")['href']
        page_url = base_url + link
        r1 = session.get(page_url,headers=headers)
        soup1=BeautifulSoup(r1.text,'lxml')
        field=soup1.find('div',{"class":"location-main"})
        location_name = field.find("h1").text
        addr = list(field.find("div",{"class":"address"}).stripped_strings)
        street_address = addr[0]
        city = addr[1].split(",")[0]
        state = addr[1].split(",")[1].strip().split(" ")[0]
        zipp = addr[1].split(",")[1].strip().split(" ")[1]
        phone = addr[2]
        if "amstar" in page_url:
            location_type = "Amstar Cinemas"
        elif "the-grand" in page_url:
            location_type = "The Grand Theatre"
        else:
            location_type = "<MISSING>"

        store=[]
        store.append(base_url if base_url else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append('US')
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type)
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append('<MISSING>')
        store.append(page_url)
        if store[2] in addressess:
            continue
        addressess.append(store[2])
        yield store

def scrape():
    # fetch_data()
    data = fetch_data()
    write_output(data)

scrape()
