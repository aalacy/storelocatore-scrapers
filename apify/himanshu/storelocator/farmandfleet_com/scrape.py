import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import re
import json
import time
# import sgzip


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
    base_url = "https://www.farmandfleet.com"
    addresses = []
    return_main_object = []
    header = {'User-agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'

              }
    
    result_coords = []
    r = session.post('https://www.farmandfleet.com/stores/', headers=header)
    soup= BeautifulSoup(r.text,'lxml')
    jsondata = json.loads(soup.find("script",{"id":"bffschema","type":"application/ld+json"}).text)
    
    for val in jsondata['location']:
        page_url = val['url']
       
        r1 = session.post(page_url, headers=header)
        soup1= BeautifulSoup(r1.text,'lxml')
        locator_domain = base_url
        location_name =  soup1.find("h1",{"class":"store-title"}).text
        street_address = val['address']['streetAddress']
        city = val['address']['addressLocality']
        state =  val['address']['addressRegion']
        zip1 =  val['address']['postalCode']
        phone =  val['telephone']
        latitude = val['geo']['latitude']
        longitude = val['geo']['longitude']
        try:
            hours = (" ".join(list(soup1.find("div",{"class":"sl-hours-list sl-store-hours"}).stripped_strings)))
        except:
            hours =''
        try:
            hours1 = (" ".join(list(soup1.find("div",{"class":"sl-hours-list sl-auto-hours"}).stripped_strings)))
        except:
            hours1 = ''
        hours_of_operation = hours + ' '+hours1
        country_code = 'US'

        location_type ="<MISSING>"
        store_number=''
        if street_address in addresses:
            continue
        addresses.append(street_address)
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zip1 if zip1 else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(hours_of_operation if hours_of_operation else '<MISSING>')
        store.append( page_url)
        #print("===", str(store))
        # return_main_object.append(store)
        yield store

  


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
