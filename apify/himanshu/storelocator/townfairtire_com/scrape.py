import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
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
    base_url = "https://www.townfairtire.com"

    soup = bs(session.get('https://www.townfairtire.com/store/tires/').text,'lxml')
    
    for atag in soup.find('div',{'class':"storeLocations"}).find_all('a'):
        
        if "Stores:" in  atag.text:
            continue
        
        page_url = base_url+atag['href']
        
        soup1 = bs(session.get(base_url+atag['href']).text,'lxml')
        latitude = json.loads(soup1.find("script",{"type":"application/ld+json"}).text)['geo']['latitude']
        longitude = json.loads(soup1.find("script",{"type":"application/ld+json"}).text)['geo']['longitude']

        main1 = list(soup1.find('div',{'class':"storeInfo"}).stripped_strings)
        address = main1[0].strip()
        ct = main1[1].strip().split(',')
        city = ct[0].strip()
        state = ct[1].strip().split(' ')[0].strip()
        zipp = ct[1].strip().split(' ')[1].strip()
        phone = soup1.find('div',{"id":"ContentPlaceHolder1_UpdatePanel2"}).find("button").text.strip()
        hour = list(soup1.find('div',{"class":"storeHours"}).stripped_strings)
        del hour[0]
        hour = ' '.join(hour)
    
        name = soup1.find('div',{"class":"tireBrand"}).find('h1').text.strip()
        
        store = []
        store.append(base_url)
        store.append(name if name else "<MISSING>")
        store.append(address if address else "<MISSING>")
        store.append(city if city else "<MISSING>")
        store.append(state if state else "<MISSING>")
        store.append(zipp if zipp else "<MISSING>")
        store.append("US")
        store.append("<MISSING>")
        store.append(phone.replace("Call ",'') if phone else "<MISSING>")
        store.append("townfairtire")
        store.append(latitude if latitude else "<MISSING>")
        store.append(longitude if longitude else "<MISSING>")
        store.append(hour if hour else "<MISSING>")
        store.append(page_url if page_url else "<MISSING>")
        
        yield store
        
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
