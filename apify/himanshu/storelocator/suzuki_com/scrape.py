import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import sgzip




def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_url ="http://suzuki.com"
    return_main_object=[]
    output=[]
    zips=sgzip.for_radius(100)
    for zp in zips:
        try:

            r = requests.get(base_url+'/DealerSearchHandler.ashx?zip='+zp+'&hasCycles=false&hasAtvs=false&hasScooters=false&hasMarine=false&hasAuto=true&maxResults=4&country=en')
            soup=BeautifulSoup(r.text,'lxml')
            for loc in soup.find_all('dealerinfo'):
                name=loc.find('name').text.strip()
                address=loc.find('address').text.strip().lower()
                city=loc.find('city').text.strip()
                state=loc.find('state').text.strip()
                zip=loc.find('zip').text.strip()
                phone=loc.find('phone').text.strip()
                country=loc.find('country').text.strip()
                storeno=loc.find('dealerid').text.strip()
                lat=loc.find('esriy').text.strip()
                lng=loc.find('esrix').text.strip()
                hour = loc.find('hoursdetails').text
                store=[]
                store.append(base_url)
                store.append(name if name else "<MISSING>")
                store.append(address if address else "<MISSING>")
                store.append(city if city else "<MISSING>")
                store.append(state if state else "<MISSING>")
                store.append(zip if zip else "<MISSING>")
                store.append(country if country else "<MISSING>")
                store.append(storeno if storeno else "<MISSING>")
                store.append(phone if phone else "<MISSING>")
                store.append("suzuki")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hour if hour.strip() else "<MISSING>")
                
                ads = address + ' ' + city + ' ' + state + ' ' + zip
                if ads not in output:
                    output.append(ads)
                    return_main_object.append(store)
        except:
            continue
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)
scrape()
