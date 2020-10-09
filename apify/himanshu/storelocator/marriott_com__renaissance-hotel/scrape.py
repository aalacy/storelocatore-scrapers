import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w', encoding="utf-8",newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", 'page_url'])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    address = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',}
    base_url = "https://renaissance-hotels.marriott.com"
    location_url = "https://renaissance-hotels.marriott.com/locations-list-view"
    r = session.get(location_url,headers=headers)
    soup = BeautifulSoup(r.text,"lxml")
    data = json.loads(soup.find(lambda tag: (tag.name == "script") and 'renaissance":{"locations":' in tag.text).text.split('(Drupal.settings,')[1].split(");")[0])['renaissance']['locations']
    for link in data:
        page_url = link['url'] 
        if "https://renaissance-hotels.marriott.com/new-york-flushing-hotel" in page_url:
            continue 
        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        try:
            location = json.loads(re.sub(r'\s+'," ",soup1.find(lambda tag:(tag.name == "script") and "addressLocality" in tag.text).text))
        except:
            continue
        street_address=''
        if "@graph" in location:
            street_address = location['@graph'][-1]['address']['streetAddress'].strip()
            location_name = location['@graph'][-1]['name']
            street_address = location['@graph'][-1]['address']['streetAddress'].strip()
            city = location['@graph'][-1]['address']['addressLocality'].strip()
            state = location['@graph'][-1]['address']['addressRegion'].strip()
            zipp = location['@graph'][-1]['address']['postalCode'].strip()
            country_code = location['@graph'][-1]['address']['addressCountry'].replace("United States","US").replace("Canada","CA").replace("USA","US")
            store_number = ""
            phone = location['@graph'][-1]['telephone']
            location_type = location['@graph'][-1]['@type']
            latitude = location['@graph'][-1]['geo']['latitude']
            longitude = location['@graph'][-1]['geo']['longitude']
            if page_url == "https://renaissance-hotels.marriott.com/new-york-flushing-hotel" or page_url == "https://renaissance-hotels.marriott.com/renaissance-new-york-chelsea-hotel" or page_url == "https://renaissance-hotels.marriott.com/renaissance-newport-beach-hotel" or page_url == "https://renaissance-hotels.marriott.com/renaissance-reno-downtown-hotel" or page_url == "https://renaissance-hotels.marriott.com/renaissance-toledo-downtown-hotel":
                country_code = "US"
            if country_code == "CA":
                state = state
                zipp = zipp
            else:
                if len(zipp.strip().split(" ")) == 2:
                    state = zipp.split(" ")[0]
                    zipp = zipp.split(" ")[1].strip()
                else:
                    state = state
                    zipp = zipp
            if country_code not in ['US','CA']:
                continue
        else:
            street_address = location['address']['streetAddress'].strip()
            location_name = location['name']
            street_address = location['address']['streetAddress'].strip()
            city = location['address']['addressLocality'].strip()
            state = location['address']['addressRegion'].strip()
            zipp = location['address']['postalCode'].strip()
            country_code = location['address']['addressCountry'].replace("United States","US").replace("Canada","CA").replace("USA","US")
            if page_url == "https://renaissance-hotels.marriott.com/new-york-flushing-hotel" or page_url == "https://renaissance-hotels.marriott.com/renaissance-new-york-chelsea-hotel" or page_url == "https://renaissance-hotels.marriott.com/renaissance-newport-beach-hotel" or page_url == "https://renaissance-hotels.marriott.com/renaissance-reno-downtown-hotel" or page_url == "https://renaissance-hotels.marriott.com/renaissance-toledo-downtown-hotel":
                country_code = "US"
            if country_code == "CA":
                state = state
                zipp = zipp
            else:
                if len(zipp.strip().split(" ")) == 2:
                    state = zipp.split(" ")[0]
                    zipp = zipp.split(" ")[1].strip()
                else:
                    state = state
                    zipp = zipp
            
            
            
            if country_code not in ['US','CA']:
                continue
            store_number = link['value']
            phone = location['contactPoint'][0]['telephone']
            location_type = location['@type']
            latitude = location['geo']['latitude']
            longitude = location['geo']['longitude']
            if street_address == "401 Chestnut Street":
                phone = "+1 215-925-0000"
        
        store = []
        store.append(base_url)
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append('<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        yield store
    
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
