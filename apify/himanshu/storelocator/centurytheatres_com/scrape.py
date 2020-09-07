import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
from datetime import datetime

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    base_url= "https://centurytheatres.com"
    headers = {           
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    
    }
    r = session.get("https://centurytheatres.com/full-theatre-list", headers=headers, verify=False)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find("div",{"class":"columnList wide"})
    for i in data.find_all("a"):

        page_url = base_url+i['href']+"#theatreInfo"
        #print(page_url)
        r1 = session.get(page_url, headers=headers, verify=False)
        soup1 = BeautifulSoup(r1.text, "lxml")
        info = soup1.find_all("script",{"type":"application/ld+json"})[-1].text
        data = json.loads(info)
        for address in  data['address']:
            street_address = address['streetAddress']
            city = address['addressLocality']
            state = address['addressRegion']
            zipp = address['postalCode']
            country_code = address['addressCountry']
        phone = data['telephone']
        location_name = data['name']
        location_type = data['@type']
        latitude = soup1.find("img",{"class":"img-responsive lazyload"})['data-src'].split("pp=")[1].split(",")[0]
        longitude = soup1.find("img",{"class":"img-responsive lazyload"})['data-src'].split("pp=")[1].split(",")[1].split("&")[0]
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)
        store.append(country_code)
        store.append("<MISSING>")
        store.append(phone if phone else "<MISSING>")
        store.append(location_type)
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append("<MISSING>")
        store.append(page_url)
        yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
