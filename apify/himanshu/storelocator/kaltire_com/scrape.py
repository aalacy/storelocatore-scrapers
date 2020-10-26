import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import unicodedata
import requests
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('kaltire_com')


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
    addressesess = []
    url = "https://www.kaltire.com/en/locations/all/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text,'lxml')
    for data in soup.find_all("a",{"class":"store-name"}):
        page_url='https://www.kaltire.com'+data['href']
        store_number = page_url.split("StoreID=")[-1]
        response1 = requests.get(page_url)
        soup1 = BeautifulSoup(response1.text,'lxml')
        name = soup1.find("p",{"class":"store-name"}).text.strip().replace("amp;",'')
        street_address = soup1.find("span",{"itemprop":"streetAddress"}).text.strip().replace("amp;",'')
        city = soup1.find("span",{"itemprop":"addressLocality"}).text.strip()
        state = soup1.find("span",{"itemprop":"addressRegion"}).text.strip()
        zip1 = soup1.find("span",{"itemprop":"postalCode"}).text.strip().replace("\nCA",'').replace("\nUS",'')
        Country = soup1.find("span",{"itemprop":"addressCountry"}).text.strip()
        phone = soup1.find("span",{"itemprop":"telephone"}).text.strip()
        latitude = soup1.find("meta",{"itemprop":"latitude"})['content']
        longitude = soup1.find("meta",{"itemprop":"longitude"})['content']
        hours = " ".join(list(soup1.find("div",{"class":"small-12 medium-6 columns store-hours"}).stripped_strings))


        # logger.info(soup1.find("p",{"class":"store-name"}))
      
        store = []
        location_type="<MISSING>"
        store.append("https://www.kaltire.com")
        store.append(name.replace("#",' # '))
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zip1 if zip1 else "<MISSING>")
        store.append(Country)
        store.append(store_number)
        store.append(phone)
        store.append(location_type if location_type else "<MISSING>")
        store.append(latitude)
        store.append(longitude)
        store.append(hours.replace("\n",' ') if hours else "<MISSING>")
        store.append(page_url)
        # store = [x.replace("–","-") if type(x) == str else x for x in store]
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addressesess:
            continue
        addressesess.append(store[2])
        # logger.info("data == "+str(store))
        # logger.info("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
        yield store

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
