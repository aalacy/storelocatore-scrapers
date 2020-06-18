import csv
from bs4 import BeautifulSoup as bs
import re
import json
from datetime import datetime
import sgzip
from sgrequests import SgRequests
session = SgRequests()
import requests

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8", newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    addresses = []
    base_url = "https://www.napaonline.com"
    headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.116 Safari/537.36',
            'accept': 'text/html, */*; q=0.01'
            }

    soup = bs(requests.get("https://www.napaonline.com/en/auto-parts-stores-near-me", headers=headers).text, "lxml")


    for link in soup.find("div",{"class":"store-browse-content"}).find_all("a"):
        state_url = base_url+link['href']

        state_soup = bs(requests.get(state_url, headers=headers).text, "lxml")
        for url in state_soup.find("div",{"class":"store-browse-content"}).find_all("a"):
            if "/en/auto-parts-stores-near-me/nc/wilmington" in url['href']:
                soup = bs(requests.get(base_url + url['href'], headers=headers).text, "lxml")
                    
                for link in soup.find_all("div",{"class":"store-browse-store-detail"}):
                    page_url = base_url + link.a['href']
                    print(page_url)
                    location_soup = bs(requests.get(page_url, headers=headers).text, "lxml")

                    data = json.loads(location_soup.find(lambda tag: (tag.name == "script" and '"streetAddress"' in tag.text)).text)
                    location_name = data['name']
                    street_address = data['address']['streetAddress']
                    city = data['address']['addressLocality']
                    state = data['address']['addressRegion']
                    zipp = data['address']['postalCode']
                    country_code = data['address']['addressCountry']
                    store_number = data['@id']
                    try:
                        phone = data['telephone']
                    except:
                        phone = "<MISSING>"
                    location_type = data['@type']
                    latitude = data['geo']['latitude']
                    longitude = data['geo']['longitude']
                    hours = ''
                    for hr in data['openingHoursSpecification']:
                        hours+= " " + hr['dayOfWeek'][0] +" "+ datetime.strptime(hr['opens'],"%H:%M:%S").strftime("%I:%M %p") +" - "+datetime.strptime(hr['closes'],"%H:%M:%S").strftime("%I:%M %p")+" "
                    
                    store = [base_url, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours.strip(), page_url]               
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    yield store
            else:
                if "(1)" in url.text:
                    
                    page_url = requests.get(base_url+url['href'],headers=headers).url
                    print(page_url)
                    location_soup = bs(requests.get(page_url, headers=headers).text, "lxml")

                    data = json.loads(location_soup.find(lambda tag: (tag.name == "script" and '"streetAddress"' in tag.text)).text)
                    location_name = data['name']
                    street_address = data['address']['streetAddress']
                    city = data['address']['addressLocality']
                    state = data['address']['addressRegion']
                    zipp = data['address']['postalCode']
                    country_code = data['address']['addressCountry']
                    store_number = data['@id']
                    try:
                        phone = data['telephone']
                    except:
                        phone = "<MISSING>"
                    location_type = data['@type']
                    latitude = data['geo']['latitude']
                    longitude = data['geo']['longitude']
                    hours = ''
                    for hr in data['openingHoursSpecification']:
                        hours+= " " + hr['dayOfWeek'][0] +" "+ datetime.strptime(hr['opens'],"%H:%M:%S").strftime("%I:%M %p") +" - "+datetime.strptime(hr['closes'],"%H:%M:%S").strftime("%I:%M %p")+" "
                    
                    store = [base_url, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours.strip(), page_url]
                    store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                    if store[2] in addresses:
                        continue
                    addresses.append(store[2])
                    yield store

                else:
                    soup = bs(requests.get(base_url + url['href'], headers=headers).text, "lxml")
                    
                    for link in soup.find_all("div",{"class":"store-browse-store-detail"}):
                        page_url = base_url + link.a['href']
                        print(page_url)
                        location_soup = bs(requests.get(page_url, headers=headers).text, "lxml")

                        data = json.loads(location_soup.find(lambda tag: (tag.name == "script" and '"streetAddress"' in tag.text)).text)
                        location_name = data['name']
                        street_address = data['address']['streetAddress']
                        city = data['address']['addressLocality']
                        state = data['address']['addressRegion']
                        zipp = data['address']['postalCode']
                        country_code = data['address']['addressCountry']
                        store_number = data['@id']
                        try:
                            phone = data['telephone']
                        except:
                            phone = "<MISSING>"
                        location_type = data['@type']
                        latitude = data['geo']['latitude']
                        longitude = data['geo']['longitude']
                        hours = ''
                        for hr in data['openingHoursSpecification']:
                            hours+= " " + hr['dayOfWeek'][0] +" "+ datetime.strptime(hr['opens'],"%H:%M:%S").strftime("%I:%M %p") +" - "+datetime.strptime(hr['closes'],"%H:%M:%S").strftime("%I:%M %p")+" "
                        
                        store = [base_url, location_name, street_address, city, state, zipp, country_code,store_number, phone, location_type, latitude, longitude, hours.strip(), page_url]               
                        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                        if store[2] in addresses:
                            continue
                        addresses.append(store[2])
                        yield store



def scrape():
    data = fetch_data()
    write_output(data)

scrape()

# "https://www.napaonline.com/api/storelocator/nearby-stores?storeType=ACMEC&location=85029&sortBy=2&language=en&page=1&distanceSearch=100"
# "https://www.napaonline.com/api/storelocator/nearby-stores?storeType=ACCOL&location=85029&sortBy=2&language=en&distanceSearch=100"
# "https://www.napaonline.com/api/storelocator/nearby-stores?storeType=ACTSC&location=85029&sortBy=2&language=en&distanceSearch=100"



Wiccan_faith@hotmail.com
