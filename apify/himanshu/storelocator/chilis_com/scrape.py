import csv
import requests
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
def fetch_data():
    addressess = []

    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
    base_url = "https://www.chilis.com"
    try:
        state_r = requests.get("https://www.chilis.com/locations/us/all",headers=headers)
    except:
        pass
    state_soup = BeautifulSoup(state_r.text, "lxml")
    for link in state_soup.find_all("a",{"class":"city-link"}):
        city_link = base_url + link['href']
        try:
            city_r = requests.get(city_link, headers=headers)
        except:
            pass
        city_soup = BeautifulSoup(city_r.text, "lxml")

        for href in city_soup.find_all("a",class_="btn slim details-btn"):
            store_link = base_url + href['href']
            try:
                store_r = requests.get(store_link, headers=headers)
            except:
                pass
            store_soup = BeautifulSoup(store_r.text, "lxml")
            data = json.loads(store_soup.find_all("script", {"type":"application/ld+json"})[1].text)
            location_name = data['name']
            street_address = data['address']['streetAddress']
            city = data['address']['addressLocality']
            state = data['address']['addressRegion']
            zipp = data['address']['postalCode']
            country_code = "US"
            store_number = data['branchCode']
            phone = data['telephone']
            location_type = data['@type']
            latitude = data['geo']['latitude']
            longitude = data['geo']['longitude']
            hours_of_operation = store_soup.find("table").text
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
            store = [x.encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]

            yield store
def scrape():
    data = fetch_data()

    write_output(data)


scrape()




        
    

