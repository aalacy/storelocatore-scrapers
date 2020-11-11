import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        for row in data:
            writer.writerow(row)
def fetch_data():
    base_url = 'https://www.citymarket.com/'
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'cache-control': 'max-age=0',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    }
    soup = bs(session.get("https://www.citymarket.com/storelocator-sitemap.xml",headers=headers).text,"lxml")
    for url in soup.find_all("loc")[:-1]:
        page_url = url.text
        location_soup = bs(session.get(page_url,headers=headers).text,"lxml")
        data = json.loads(str(location_soup.find("script",{"type":"application/ld+json"})).split(">")[1].split("<")[0])
        location_name = location_soup.find("h1",{"data-qa":"storeDetailsHeader"}).text.strip()
        street_address = data['address']['streetAddress']
        city = data['address']['addressLocality']
        state = data['address']['addressRegion']
        zipp = data['address']['postalCode']
        country_code = "US"
        store_number = page_url.split("/")[-1]
        phone = data['telephone']
        location_type = data['@type']
        lat = data['geo']['latitude']
        lng = data['geo']['longitude']
        f = (data['department'])
        data_h  = ''
        for h in f:
            if "openingHours" in h:
                data_h = " ".join(h['openingHours'])
        hours = (" ".join(data['openingHours']))+", Pharmacy hours : "+ data_h
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
        store.append(lat)
        store.append(lng)
        store.append(hours.replace("Su-Sa","Sun - Sat :").replace("-00:00"," - Midnight").replace("Su","Sun").replace("Mo-Fr","Mon - Fri").replace("Sa","Sat"))
        store.append(page_url)
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store
        
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
