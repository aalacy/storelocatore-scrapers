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
    base_url = "https://www.karateamerica.info"
    return_main_object=[]
    r = session.get(base_url+'/location')
    soup=BeautifulSoup(r.text,'lxml')
    output=[]
    main=soup.find_all('script')
    for dt in main:
        if "var map2" in dt.text:
            dt1=json.loads(dt.text.split('$("#map2").maps(')[1].split(').data')[0])
            for loc in dt1['places']:
                name=loc['title']
                address=loc['address']
                city=loc['location']['city']
                state=loc['location']['state']
                lat=loc['location']['lat']
                lng=loc['location']['lng']
                country="US"
                zip=loc['location']['postal_code']
                phone=loc['location']['extra_fields']['phone']
                hour=''
                storeno=loc['id']
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
                store.append("karateamerica")
                store.append(lat if lat else "<MISSING>")
                store.append(lng if lng else "<MISSING>")
                store.append(hour if hour.strip() else "<MISSING>")
                if zip not in output:
                    output.append(zip)
                    return_main_object.append(store)
    return return_main_object

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
