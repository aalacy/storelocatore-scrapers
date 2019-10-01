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
    base_url ="https://www.mitsubishicars.com"
    return_main_object=[]
    output=[]
    zps=sgzip.for_radius(50)
    for zp in zps:
       
      
        # while(True):
        #     try:
        #         r=requests.get('https://www.mitsubishicars.com/rs/dealers?bust=1569242590201&zipCode='+zp+'&idealer=false&ecommerce=false').json()
        #         break
        #     except:

        try:
            r=requests.get('https://www.mitsubishicars.com/rs/dealers?bust=1569242590201&zipCode='+zp+'&idealer=false&ecommerce=false').json()        

            for loc in r:
                if loc['zipcode']:
                    address=loc['address1'].strip()
                    if loc['address2']:
                        address+=' '+loc['address2'].strip()
                    name=loc['dealerName'].strip()
                    city=loc['city'].strip()
                    state=loc['state'].strip()
                    zip=loc['zipcode']
                    phone=loc['phone'].strip()
                    country=loc['country'].strip()
                    if country=="United States":
                        country="US"
                    lat=loc['latitude']
                    lng=loc['longitude']
                    hour=''
                    storeno=loc['bizId']
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
                    store.append("mitsubishicars")
                    store.append(lat if lat else "<MISSING>")
                    store.append(lng if lng else "<MISSING>")
                    store.append(hour if hour.strip() else "<MISSING>")
                    adrr =name+' '+address + ' ' + city + ' ' + state + ' ' + str(zip)
                    if adrr not in output:
                        output.append(adrr)
                        yield store
        except:
            continue
def scrape():
    data = fetch_data()
    write_output(data)
scrape()
