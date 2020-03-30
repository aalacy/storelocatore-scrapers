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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url = "https://fcer.com"
    r = session.get(base_url+"/locations")
    soup = BeautifulSoup(r.text,"lxml")
    return_main_object = []
    main = soup.find('section',{"class":"metro_map"}).find_all('section',{"class":"metro_location"})
    for location in main:
        for atag in location.find_all('a'):
            if 'er-express' not in atag['href']:
                r1 = session.get(base_url+atag['href'])
                soup1= BeautifulSoup(r1.text,"lxml")
                name=location.find('div',{"class":"metro_info"}).find('h4').text.strip()
                main1=json.loads(soup1.find('script',{'type':"application/ld+json"}).text)
                store=[]
                store.append("https://fcer.com")
                store.append(name)
                store.append(main1['address']['streetAddress'])
                store.append(main1['address']['addressLocality'])
                store.append(main1['address']['addressRegion'])
                store.append(main1['address']['postalCode'])
                store.append('US')
                store.append("<MISSING>")
                store.append(main1['telephone'])
                store.append("Fcer")
                store.append(main1['geo']['latitude'])
                store.append(main1['geo']['longitude'])
                store.append(main1['openingHours'])
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
