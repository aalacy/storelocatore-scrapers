import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import io
import unicodedata
import json


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36'
    }
    base_url = "https://www.wework.com/locations"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    for country in ['US','CA']:

        for city in soup.find("div",{"class":"markets-list__country markets-list__country--"+str(country)}).find_all("a"):
            
            city_request = session.get("https://www.wework.com" + city["href"],headers=headers)
            city_soup = BeautifulSoup(city_request.text,"lxml")
            for locaion in city_soup.find_all("a",{"class":'ray-card'}):
                page_url = "https://www.wework.com" + locaion["href"]
                location_request = session.get(page_url,headers=headers)
                location_soup = BeautifulSoup(location_request.text,"lxml")
                json_data = json.loads(str(location_soup.find("script",{"type":"application/ld+json"})).split(">")[1].split("<")[0])['@graph'][-1]
                
                city = json_data["address"]["addressLocality"]
                zipp = json_data["address"]["postalCode"]
                addr = json_data["address"]["streetAddress"].replace(city,"|").replace(zipp,"").strip()
                street_address = addr.split("|")[0].strip()
                state = addr.split("|")[1].strip()

                store = []
                store.append("https://www.wework.com")
                store.append(location_soup.find("h1",{"id":'heading'}).text.strip())
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append(json_data["address"]["addressCountry"])
                store.append("<MISSING>")
                store.append(json_data["telephone"])
                store.append(json_data["brand"])
                store.append(json_data["geo"]["latitude"])
                store.append(json_data["geo"]["longitude"])
                store.append("<MISSING>")
                store.append(page_url)
                store = [str(x).replace("–","-").encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
                yield store

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
