import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup

import time
from random import randint
import re

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
HEADERS = {'User-Agent' : user_agent}

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    base_link = 'https://www.figandolive.com/'

    req = session.get(base_link, headers = HEADERS)
    time.sleep(randint(1,2))
    try:
        item = BeautifulSoup(req.text,"lxml")
    except (BaseException):
        print('[!] Error Occured. ')
        print('[?] Check whether system is Online.')

    lis = item.find(class_="sub-menu").find_all('li')
    link_list = []
    for li in lis:
        link_list.append("https://www.figandolive.com" + li.a['href'])

    all_store_data = []

    for link in link_list:

        req = session.get(link, headers = HEADERS)
        print(link)
        time.sleep(randint(1,2))
        try:
            item = BeautifulSoup(req.text,"lxml")
        except (BaseException):
            print('[!] Error Occured. ')
            print('[?] Check whether system is Online.')

        locator_domain = "figandolive.com"
        raw_name = item.find(class_="hero__content container").text
        location_name = raw_name[:raw_name.find("View")].replace("\n"," ").strip()

        phone_number = item.find('a', attrs={'data-bb-track-category': "Phone Number"})['href'].replace("tel:","")
        address = item.find(class_="gmaps")['data-gmaps-address'].split(',')

        main = item.find('section', {'id': 'intro'})
        ps = main.find_all('p')

        hours = ''
        for i, p in enumerate(ps):
            if '00pm' in p.text or '00am' in p.text or 'Closed' in p.text:
                hours += p.text + ' '

        hours = hours.strip()
        if len(address) == 4:
            if address[0].strip():
                street_address = (address[0] + address[1])
            city = address[2].strip()
            state_zip = address[3].strip().split(' ')

            state = state_zip[0]
            zip_code = state_zip[1]
        else:
            street_address = address[0]
            city = address[1].strip()
            state_zip = address[2].strip().split(' ')

            state = state_zip[0]
            zip_code = state_zip[1]

        street_address = re.findall("[0-9].+", street_address)[0].strip()
        lat = item.find(class_="gmaps")['data-gmaps-lat']
        longit = item.find(class_="gmaps")['data-gmaps-lng']

        store_number = '<MISSING>'
        location_type = '<MISSING>'
        country_code = 'US'
        store_data = [locator_domain, link, location_name, street_address, city, state, zip_code, country_code,
                      store_number, phone_number, location_type, lat, longit, hours]
        all_store_data.append(store_data)

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
