import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
import requests
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    }
    base_url = "http://essentiahealth.org"
    r = session.get("https://www.essentiahealth.org/find-facility/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for page in soup.find("div",{"class":"Pagination"}).find_all("option"):
        r1 = session.get(page['value'].replace("~",base_url))
        soup1 = BeautifulSoup(r1.text, "lxml")
        for script in soup1.find("div",{"class":"LocationsList"}).find_all("script"):
            data = json.loads(script.text)

            location_name = data['name']
            street_address = data['address']['streetAddress'].replace("Floor","").split("Suite")[0].replace(",","").strip()
            city = data['address']['addressLocality']
            state = data['address']['addressRegion']
            zipp = data['address']['postalCode']
            try:
                phone = data['contactPoint']['telephone']
            except:
                phone = "<MISSING>"
            latitude = data['geo']['latitude']
            longitude = data['geo']['longitude']
            if "http" in script.find_next("li").find("a",{"class":"Name"})['href']:
                page_url = script.find_next("li").find("a",{"class":"Name"})['href']
            else:
                page_url = base_url + script.find_next("li").find("a",{"class":"Name"})['href']
            r2 = session.get(page_url)
            soup2 = BeautifulSoup(r2.text, "lxml")
            try:
                hours = " ".join(list(soup2.find("div",{"class":"HoursContent"}).find("p").stripped_strings))
            except:
                hours = "<MISSING>"
    
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append("US")
            store.append("<MISSING>")
            store.append(phone)
            store.append("<MISSING>")
            store.append(latitude)
            store.append(longitude)
            store.append(hours)
            store.append(page_url)
            if store[2] in addresses:
                continue
            addresses.append(store[2])
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
            # print("data == "+str(store))
            # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            yield store
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
