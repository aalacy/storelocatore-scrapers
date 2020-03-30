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
    base_url = "https://www.slapfishrestaurant.com"
    return_main_object=[]
    r = session.get(base_url+'/locations')
    soup=BeautifulSoup(r.text,'lxml')
    main=soup.find_all('script',type="text/javascript")
    for script in main:
        if "var jsonContent" in script.text:
            main1=json.loads(script.text.split('var jsonContent = ')[1].split('};')[0]+'}',strict=False)
            for loc in main1['data']:
                address=loc['street_number']+' '+loc['address_route'].strip()
                city=loc['city'].strip()
                state=loc['state'].strip()
                zip=loc['postal_code'].strip()
                phone=loc['phone'].strip()
                name=loc['title'].strip()
                lat=loc['lat']
                lng=loc['lng']
                storeno=loc['id']
                country=loc['country']
                if country=="United States":
                    country="US"
                hour=loc['hours']
                cleanr = re.compile('<.*?>')
                hour = re.sub(cleanr, '', hour)
                hour = re.sub(r'\s+', '', hour)
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
                store.append("slapfishrestaurant")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hour if hour.strip() else "<MISSING>")
                return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
