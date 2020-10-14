import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)
session = SgRequests()
def fetch_data():
    addressess = []
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.chilis.com"
    state_r = session.get("https://www.chilis.com/locations/us/all",headers=headers)
    state_soup = BeautifulSoup(state_r.text, "lxml")
    for link in state_soup.find_all("a",{"class":"city-link"}):
        city_link = base_url + link['href']
        city_r = session.get(city_link, headers=headers)
        city_soup = BeautifulSoup(city_r.text, "lxml")
        for href in city_soup.find_all("a",class_="btn slim details-btn"):
            store_link = base_url + href['href']
            store_r = session.get(store_link, headers=headers)
            store_soup = BeautifulSoup(store_r.text, "html5lib")
            data = json.loads(store_soup.find_all("script", {"type":"application/ld+json"})[1].text)
            location_name = data['name'].replace("&#39;","'").replace("&amp;","")
            street_address = data['address']['streetAddress'].replace("&#39;","'").replace("A&amp;B","A&B").replace("&amp;","")
            city = data['address']['addressLocality'].replace("&#39;","'").replace("&amp;","")
            state = data['address']['addressRegion'].replace("&#39;","'").replace("&amp;","")
            zipp = data['address']['postalCode']
            country_code = "US" 
            store_number = "<MISSING>"
            phone = data['telephone']
            location_type = data['@type']
            latitude = data['geo']['latitude']
            longitude = data['geo']['longitude']
            hours_of_operation = store_soup.find("table").text.strip()
            page_url = data['url'] 

            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number) 
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store

    ca_r = session.get("https://www.chilis.com/locations/ca/all",headers=headers)
    ca_soup = BeautifulSoup(ca_r.text, "lxml")
    for link in ca_soup.find_all("a",{"class":"city-link"}):
        city_link = base_url + link['href']
        city_r = session.get(city_link, headers=headers)
        city_soup = BeautifulSoup(city_r.text, "lxml")
        jd = json.loads(str(city_soup).split("locationsList:")[1].split("};window.Chilis.Strings")[0])
        for value in jd:

            location_name = value['name'].replace("&amp;","")
            street_address = value['address'].replace("&amp;","")
            city = value['city'].replace("&amp;","")
            state = value['state'].replace("&amp;","")
            zipp = value['zipCode']
            country_code = "CA" 
            store_number = "<MISSING>"
            phone = value['phone']
            location_type = "Restaurant"
            latitude = value['latitude']
            longitude = value['longitude']
            hours_of_operation = "<MISSING>"
            page_url = city_link
            store = []
            store.append(base_url)
            store.append(location_name)
            store.append(street_address)
            store.append(city)
            store.append(state)
            store.append(zipp)
            store.append(country_code)
            store.append(store_number) 
            store.append(phone)
            store.append(location_type)
            store.append(latitude)
            store.append(longitude)
            store.append(hours_of_operation)
            store.append(page_url)
            store = [x.replace("–","-") if type(x) == str else x for x in store]
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if type(x) == str else x for x in store]
            if store[2] in addressess:
                continue
            addressess.append(store[2])
            yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()




        
    


