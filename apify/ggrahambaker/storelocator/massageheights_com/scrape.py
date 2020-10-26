import csv
import os, re
from sgrequests import SgRequests
import json
from bs4 import BeautifulSoup

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    locator_domain = 'https://www.massageheights.com'
    ext = '/locations/?CallAjax=GetLocations'
    to_scrape = locator_domain + ext
    page = session.get(to_scrape)
    assert page.status_code == 200

    locs = json.loads(page.content)
    all_store_data = []
    
    pattern = re.compile(r'\s\s+') 
    for a in locs:
        location_name = a['FranchiseLocationName']
        street_address = a['Address1']
        street_address += ' ' + a['Address2']
        city = a['City']
        state = a['State']
        zip_code = a['ZipCode']
        phone_number = a['Phone']
        lat = a['Latitude']
        longit = a['Longitude']

        location_hours = a['LocationHours']
        
        
        page_url = locator_domain + a['Path']
        #print(page_url)
        page = session.get(page_url)
        soup = BeautifulSoup(page.text,'html.parser')
        flag = 0 
        try:
            hours = soup.find('div',{'class':'hero-hours'}).text
            hours = re.sub(pattern,'' ,hours).replace('Hours','').replace('PM','PM ').replace('\n','')
        except:
            if soup.find('h4').text == 'Coming Soon!':
                flag = 1
            else:
                hours = '<MISSING>'
                
            
        
        country_code = 'US'
        store_number = '<MISSING>'
        location_type = '<MISSING>'
        if flag == 0:
            store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code,
                        store_number, phone_number, location_type, lat, longit, hours, page_url]
            all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
