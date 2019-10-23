import csv
import requests
from bs4 import BeautifulSoup
import re
import json


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
  
    base_url= "https://www.dicarlospizza.com/order"
    r = requests.get(base_url)
    soup= BeautifulSoup(r.text,"lxml")
  
    jj= []
    k = (soup.find_all("div",{"class":"sqs-col-4"}))
    for x in k:
        for y in x.find_all('div',{'class':'sqs-block-html'}):
            locator_domain  = 'https://www.dicarlospizza.com/'
            location_name = y.find('h3').text.strip()

            street_address = y.find('p')
            cnv  = str(street_address).replace('<br/>','%%')
            jj.append(soup.find_all('script', {'type': 'application/ld+json'}))
            soup = BeautifulSoup(cnv, "lxml")
            street_address = soup.text.split('%%')[0]

            if location_name == 'STEUBENVILLE*':

                db = json.loads(jj[0][2].text)

                street_address = db['address'].split('\n')[0] + ' ' + db['address'].split('\n')[1].strip().split(',')[0]



            phone = ''
            if '.' in soup.text.split('%%')[1]:
                phone  = soup.text.split('%%')[1]

            city = ''
            state = ''
            zip = ''
            country_code = 'US'
            store_number = ''
            location_type = ''
            latitude = ''
            longitude = ''
            hours_of_operation = ''
            page_url = base_url



            store = []

            store.append(locator_domain if locator_domain else '<MISSING>')
            store.append(location_name if location_name else '<MISSING>')
            store.append(street_address if street_address else '<MISSING>')
            store.append(city if city else '<MISSING>')
            store.append(state if state else '<MISSING>')
            store.append(zip if zip else '<MISSING>')
            store.append(country_code if country_code else '<MISSING>')
            store.append(store_number if store_number else '<MISSING>')
            store.append(phone if phone else '<MISSING>')
            store.append(location_type if location_type else '<MISSING>')
            store.append(latitude if latitude else '<MISSING>')
            store.append(longitude if longitude else '<MISSING>')

            store.append(hours_of_operation if hours_of_operation else '<MISSING>')
            store.append(page_url if hours_of_operation else '<MISSING>')

            # print("data====",str(store))
            yield store

def scrape():
    data = fetch_data()
    write_output(data)


scrape()




