import csv
import requests
from bs4 import BeautifulSoup
import re
import json
from sgrequests import SgRequests
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8") as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    headers = {
             'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',    
    }

    base_url = "https://www.place.hyatt.com/"     
    r = session.get("https://www.hyatt.com/local", headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    links = soup.find_all("a",{"class":"book-now-btn b-button b-button-browse-ol b-button_height-mini b-button_icon-newwinb-mt2@md"})

    for link in links:

        page_url = link['href']
        r1 = requests.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        json_data = json.loads(soup1.find("script", {"type":"application/ld+json"}).text)
    
        location_name = json_data['name']
        street_address = json_data['address']['streetAddress'].replace("\t","").strip()
        city = json_data['address']['addressLocality']
        state = json_data['address']['addressRegion']
        zipp = json_data['address']['postalCode']
        country_code = json_data['address']['addressCountry'] 
        location_type = json_data['@type']
        phone = json_data['telephone']
        latitude = json_data['geo']['latitude']
        longitude = json_data['geo']['longitude']
        
    
        store = []
        
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp if zipp else "<MISSING>")   
        store.append(country_code)
        store.append("<MISSING>")
        store.append(phone)
        store.append(location_type)
        store.append(latitude )
        store.append(longitude )
        store.append("<MISSING>")
        store.append(page_url)
        # print("data==="+str(store))
        # print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~`")

        yield store
    

        


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
