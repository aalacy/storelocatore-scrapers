
import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
import re
import json
import time
import pgeocode
session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w', newline='') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data(): 
    addresses = []
    base_url = "https://www.toyota.co.uk/"
    soup = session.get("https://www.toyota.co.uk/api/dealer/drive/-0.1445783/51.502436?count=1000&extraCountries=im|gg|je&isCurrentLocation=false").json()
    for data in soup['dealers']:
        street_address1=''
        location_name = data['name']
        street_address1 = data['address']['address1'].strip()
        if street_address1:
            street_address1=street_address1
        street_address =street_address1+ ' '+ data['address']['address'].strip()
        city = data['address']['city']
        zipp = data['address']['zip']
        phone = data['phone']
      
        if "Newbridge" in street_address:
            street_address =  "2 Lonehead Drive"
            city = "Newbridge"
            state = "Edinburgh"
        lat = data['address']['geo']['lat']
        lng = data['address']['geo']['lon']
        page_url = data['url']
    
        
        hour_url = page_url.replace(".uk/",".uk")+"/about-us#anchor-views-opening_hours-block_3"
        if page_url == "http://burystedmunds.toyota.co.uk/":
            hour_url = "https://turnersburystedmunds.toyota.co.uk/about-us#anchor-views-opening_hours-block_3"
        
        
        if page_url == "https://www.toyota.co.uk/dealer/Bournemouth/BH23%201EZ/Hendy%20Toyota%20(Christchurch)":
            hours = "<MISSING>"
        else:
            location_soup = bs(session.get(hour_url).text, "lxml")
            if data['address']['_region']:
                state = data['address']['_region']
            else:
                try:
                    state = json.loads(location_soup.find(lambda tag: (tag.name == "script") and "jQuery.extend(Drupal.settings" in tag.text).text.split("jQuery.extend(Drupal.settings,")[1].split("//--><!]]>")[0].replace(");",""))['gmap']['auto1map']['markers'][0]['text'].split('"state">')[1].split("<")[0]
                except:
                    state =  pgeocode.Nominatim('GB').query_postal_code(zipp)['county_name']
            try:
                try:
                    hours = " ".join(list(location_soup.find("fieldset" ,{"class":"sales views-fieldset"}).stripped_strings))
                except:
                    hours = " ".join(list(location_soup.find("fieldset" ,{"class":"service views-fieldset"}).stripped_strings))
            except:
                hours = "<MISSING>"
        if state == "City of Edinburgh":
            state = "Edinburgh"
        if state == "County of Bristol":
            state = "Bristol"            
        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append("UK")
        store.append("<MISSING>")
        store.append(phone)
        store.append("<MISSING>")
        store.append(lat)
        store.append(lng)
        store.append(hours)
        store.append(page_url if page_url else "<MISSING>")     
    
        store = [str(x).encode('ascii', 'ignore').decode('ascii').strip() if x else "<MISSING>" for x in store]
        if store[2] in addresses:
            continue
        addresses.append(store[2])
        yield store

     
    
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()

"https://turnersburystedmunds.toyota.co.uk/about-us#anchor-views-opening_hours-block_3"
"http://burystedmunds.toyota.co.uk//about-us#anchor-views-opening_hours-block_3"
