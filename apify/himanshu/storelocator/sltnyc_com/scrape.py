import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://sltnyc.com/"
    r = session.get("https://sltnyc.com/studios/", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    
    for link in soup.find_all("a",{"class":"button-outline-secondary studio-grid__button"}):
        if "at-home" in link['href']:
            continue
        page_url = link['href']

        location_soup = BeautifulSoup(session.get(page_url).text, "lxml")
        location_name = location_soup.find("h1",{"class":"hero__headline"}).text.strip()
        data = list(location_soup.find("div",{"class":"wysiwyg hero__direction-content"}).stripped_strings)
        
        street_address = data[0]
        city = data[1].split(",")[0]
        state = " ".join(data[1].split(",")[1].split()[:-1])
        zipp = data[1].split(",")[1].split()[-1]
        phone = data[-1].replace(".","")
    
        if "@" in location_soup.find('a', {'class', 'hero__direction-link'}).get('href'):
            latitude = location_soup.find('a', {'class', 'hero__direction-link'}).get('href').split('@')[1].split(',')[0]
            longitude = location_soup.find('a', {'class', 'hero__direction-link'}).get('href').split('@')[1].split(',')[1]
        else:
            latitude = "<MISSING>"
            longitude = "<MISSING>"
        
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
        store.append("SLT")
        store.append(latitude)
        store.append(longitude)
        store.append("<MISSING>")
        store.append(page_url)
        yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
