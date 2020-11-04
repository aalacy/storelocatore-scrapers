import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
# from selenium import webdriver


session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://www.loccitane.com/"
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36',
    }
    # driver = webdriver.Chrome(executable_path='chromedriver.exe')
    r = session.get("https://www.loccitane.com/on/demandware.store/Sites-OCC_US-Site/en_US/Stores-GetStores", headers=headers).json()
    
    for data in r['stores']:
        location_name = data['name']
        street_address = data['address1']
        city = data['city']
        state = data['stateCode']
        zipp = data['postalCode']
        country_code = "US"
        store_number = "<MISSING>"
        phone = data['phone']
        location_type = data['custom']['OCC_category']
        latitude = data['latitude']
        longitude = data['longitude']
        page_url = "https://www.loccitane.com/on/demandware.store/Sites-OCC_US-Site/en_US/Stores-ShowStore?id="+str(data['ID'])

        r1 = session.get(page_url, headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")
        if soup1.find("div",{"class":"m-week-hours"}):
            hours_of_operation = " ".join(list(soup1.find("div",{"class":"m-week-hours"}).stripped_strings))
        else:
            hours_of_operation = "<MISSING>"
    
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
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store 

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
