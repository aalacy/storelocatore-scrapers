import csv
import os
import re, time
import requests
from bs4 import BeautifulSoup

def write_output(data):
    with open('data.csv', mode='wb') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            if row:
                writer.writerow(row)
def fetch_data():
    store_no=[];data=[]
    url ="https://www.myeyelab.com/locations/"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    script = soup.findAll('script')
    json=re.findall(r'loc_data\s*=(.*?)]\'\);',str(script))
    street_address=re.findall(r'sl_address":"(.*?)","', str(json))
    for n in range(0,len(street_address)):
        try:
            store_no.append(street_address[n].split("#")[1])
        except:
            store_no.append('<MISSING>')
    location_name = re.findall(r'sl_web_name":"(.*?)","', str(json))
    state = re.findall(r'sl_state":"(.*?)","', str(json))
    city=re.findall(r'sl_city":"(.*?)","', str(json))
    zipcode =re.findall(r'sl_zip":"(.*?)"\}', str(json))
    latitude =re.findall(r'lat":"(.*?)","', str(json))
    longitude =re.findall(r'lng":"(.*?)","', str(json))
    for n in range(0,len(location_name)): 
        data.append([
            'https://www.myeyelab.com',
            location_name[n],
            street_address[n],
            city[n],
            state[n],
            zipcode[n],
            'US',
            store_no[n],
            '<MISSING>',
            '<MISSING>',
            latitude[n],
            longitude[n],
            '<MISSING>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)
   
scrape()
