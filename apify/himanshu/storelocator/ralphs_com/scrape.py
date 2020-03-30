import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL)

        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])

        # print("data::" + str(data))
        for i in data:
            writer.writerow(i)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    }
 
    r = session.get("https://www.ralphs.com/storelocator-sitemap.xml", headers=headers)    
    soup = BeautifulSoup(r.text, "lxml")
    link1 = soup.find_all('loc')[:-1]
    for i in link1:
        link = i.text
        r1= session.get(link, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        main1=soup1.find('div', {'class': 'StoreAddress-storeAddressGuts'})
        if main1 == None:
            continue
        data = json.loads(soup1.find(lambda tag: (tag.name == "script") and "openingHours" in tag.text).text)
        location_name = data['name']
        street_address = data['address']['streetAddress']
        city = data['address']['addressLocality']
        state = data['address']['addressRegion']
        zipp = data['address']['postalCode']
        store_number = link.split("/")[-1]
        location_type = data['@type']
        latitude = data['geo']['latitude']
        longitude = data['geo']['longitude']
        phone = soup1.find('span', {'class': 'PhoneNumber-phone'}).text
        hour = soup1.find('div', {'class': 'StoreInformation-storeHours'}).text
        location_name = soup1.find('h1', {'class': 'StoreDetails-header'}).text
        store=[]           
        store.append('https://www.ralphs.com/')
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state) 
        store.append(zipp)
        store.append('US')
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hour)
        store.append(link)
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        # print("data =="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")
        yield store
        

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
