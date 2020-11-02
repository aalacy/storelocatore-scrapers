import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
session = SgRequests()
def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)
def fetch_data():
    page_url1 = "https://www.honeygrow.com/"
    base_url= "https://www.honeygrow.com/"
    r = session.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
    data = soup.find("script",{"type":"application/ld+json"}).text
    json_data = json.loads(data)
    data_8 = (json_data['subOrganization'])
    for i in data_8 :
        phone = (i['telephone'])
        street_address = i['address']['streetAddress']
        city = i['address']['addressLocality']
        state = i['address']['addressRegion']
        zipp = i['address']['postalCode']
        location_name = i['address']['name']
        page_url = i['url']
        r1 = session.get(page_url)
        soup1= BeautifulSoup(r1.text,"lxml")
        longitude = (soup1.find("div",{"class":"gmaps"})['data-gmaps-lng'])
        latitude = (soup1.find("div",{"class":"gmaps"})['data-gmaps-lat'])
        hours_of_operation = soup1.find_all("div",{"class":"col-md-6"})[0].text.replace("NOW OPEN!","").replace("day","day ").replace("Located in Ellisburg Shopping Center","").split('\n')[-2]
        hours_of_operation = (re.sub(' +', ' ', hours_of_operation)).strip()
        if "CLOSED until further notice" in hours_of_operation:
            hours_of_operation = "CLOSED until further notice"

        store=[]
        store.append(page_url1 if page_url1 else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append('US')
        store.append('<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append('<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation.replace('CLOSED'," CLOSED").replace('ON JULY 4TH',"").strip()  if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        yield store 
def scrape():
    data = fetch_data()
    write_output(data)
scrape()


