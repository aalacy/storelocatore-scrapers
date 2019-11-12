import csv
import requests
from bs4 import BeautifulSoup
import re
import json
import ast

def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation","page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    return_main_object = []
    addresses = []
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36',
    'Accept' :'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3'
    }
    base_url = locator_domain= 'http://napoleonsbakery.com/'
    page_url= "http://napoleonsbakery.com/locations.php"
    r = requests.get(page_url,headers=headers)
    soup= BeautifulSoup(r.text,"lxml")

    for loc in soup.find('div',{'id':'location'}).find_all('div',{'id':'single'}):
        for p in loc.find_all('p',class_='bodytext'):
            ch = p.strong.text.split('-')
            city = ch[0].replace('*','').strip()
            location_name = city
            state = loc.h4.text.strip()
            if "Honolulu" == state:
                city  = state
                state = "<MISSING>"
            
            if len(ch) == 2:
                hours_of_operation = ch[-1].strip()
            else:
                hours_of_operation = "<MISSING>"
            zipp = "<MISSING>"
            country_code = "US"
            store_number = "<MISSING>"
            latitude = "<MISSING>"
            longitude = "<MISSING>"
            location_type = "<MISSING>"
            street_address = p.strong.nextSibling.nextSibling.strip()
            phone = list(p.stripped_strings)[-1].strip()
            
            store = [locator_domain, location_name, street_address, city, state, zipp, country_code,
            store_number, phone, location_type, latitude, longitude, hours_of_operation, page_url]
            store = [x if x else "<MISSING>" for x in store]

            if store[2] in addresses:
                continue
            addresses.append(store[2])

            # print("data = " + str(store))
            # print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            return_main_object.append(store)

    return return_main_object


def scrape():
    data = fetch_data()
    write_output(data)


scrape()


