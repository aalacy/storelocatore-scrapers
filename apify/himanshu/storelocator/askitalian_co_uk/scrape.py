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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36',
    'token': '5967R219L5JmvS3P28718916UwER2Y4qx285hHCM90lU0I10537Eol8N8xk0311N'
    
    }
    base_url = "https://www.askitalian.co.uk/"
    page_api = "https://www.askitalian.co.uk/api/restaurant/list"
    json_data = session.post(page_api, headers=headers).json()

    for value in json_data['data']:
        location_name = value['name']
        address = value['address'].split(",")
        if len(address) == 3:
            street_address = address[0]
            city = address[1]
            state = "<MISSING>"

        elif ' Kent' in address:
            state = 'Kent'
            street_address = address[0]
            city = address[1]

        elif len(address) == 4:
            city = address[-2]
            street_address = ''.join(address[:2])
            state = "<MISSING>"

        elif ' Essex' in address:
            city = address[-3]
            street_address = ''.join(address[:2])
            state = 'Essex'

        elif ' Norwich' in address:
            city = 'Norwich'
            street_address = ''.join(address[:2])
            state = "<MISSING>"

        elif len(address) == 5:
            city = address[-2]
            street_address = ''.join(address[:3])
            state = "<MISSING>"
        
        elif len(address) == 6:
            city = address[-2]
            street_address = ''.join(address[:4])
            state = "<MISSING>"


        zipp = address[-1]
        country_code = "UK"
        store_number = "<MISSING>"
        phone = value['telephone']
        location_type = "Restaurant"
        latitude = value['latitude']
        longitude = value['longitude']

        page_url = "https://www.askitalian.co.uk" + value['url']
        r = session.get(page_url,headers=headers)
        soup = BeautifulSoup(r.text,"lxml")
        hour_data = soup.find_all("p",{"itemprop":"openingHours"})
        hours = []
        for j in hour_data[::2]:
            hours.append(j.text)
        hours_of_operation = ','.join(hours)


        store = []
        store.append(base_url)
        store.append(location_name)
        store.append(street_address)
        store.append(city)
        store.append(state)
        store.append(zipp)   
        store.append(country_code)
        store.append(store_number)
        store.append(phone)
        store.append(location_type)
        store.append(latitude)
        store.append(longitude)
        store.append(hours_of_operation)
        store.append(page_url)
    
        store = [str(x).strip() if x else "<MISSING>" for x in store]
        yield store


def scrape():
    data = fetch_data()
    write_output(data)

scrape()