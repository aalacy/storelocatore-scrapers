import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import re

import time
from random import randint

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)

def fetch_data():
    cookie = {'PHPSESSID':'o4to3hi0sg7bf2qepj5casic44'}
    session = SgRequests()
    HEADERS = { 'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36' }

    all_store_data = []
    last_seen = 0
    for i in range(300):
        url = 'https://globalpetfoods.com/store-locations/s/?st=' + str(i)
        if i > 200 and (i - last_seen > 20):
            break

        locator_domain = 'https://globalpetfoods.com/'
        r = session.get(url, headers = HEADERS, cookies=cookie)
        soup = BeautifulSoup(r.content, 'html.parser')

        location_name = soup.find('span', {'class': 'location_title'}).text.strip()
        if location_name == '':
            continue

        if 'Opening' in location_name:
            continue

        print(url)
        raw_json = soup.find('script', {'type': 'application/ld+json'}).text.replace('\r\n', '').replace("\\\\\\\'", "'")
        formatted_json = raw_json.replace("\\", "").replace('<a href="https://miramichi.globalpetfoods.com/" target="_blank">SHOP NOW!</a>',"")

        loc_json = json.loads(formatted_json)
        
        hours = ''
        
        for h in loc_json['openingHours']:
            hours += h + ' '
            
        hours = hours.strip()
        
        addy = loc_json['address']
        city = addy['addressLocality']
        state = addy['addressRegion']
        zip_code = addy['postalCode']
        if zip_code == "HN8 1X7":
            zip_code = "H8N 1X7"
        street_address = addy['streetAddress']
        phone_number = addy['telephone'].replace('=', '').replace('+1', '').strip()
        if phone_number == '':
            phone_number = '<MISSING>'
        location_name = addy['name']

        country_code = 'CA'
        
        store_number = i
        location_type = '<MISSING>'

        map_link = soup.find(class_="location_directions").a['href']
        req = session.get(map_link, headers = HEADERS)
        time.sleep(randint(1,2))
        try:
            maps = BeautifulSoup(req.text,"lxml")
        except (BaseException):
            print('[!] Error Occured. ')
            print('[?] Check whether system is Online.')

        try:
            raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
            lat = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
            longit = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
        except:
            lat = "<MISSING>"
            longit = "<MISSING>"

        if len(lat) > 20 or not longit:
            lat = raw_gps[raw_gps.rfind("=")+1:raw_gps.find(",")].strip()
            longit = raw_gps[raw_gps.rfind("-"):].strip()
        if not lat[3:5].isnumeric() or not longit[5:7].isnumeric():
            lat = "<MISSING>"
            longit = "<MISSING>"

        page_url = url
        store_data = [locator_domain, location_name, street_address, city, state, zip_code, country_code, 
                    store_number, phone_number, location_type, lat, longit, hours, page_url]

        all_store_data.append(store_data)
        last_seen = i

    return all_store_data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
