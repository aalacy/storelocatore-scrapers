from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re

BASE_URL = 'https://www.softsurroundings.com'
MISSING = '<MISSING>'
INACCESSIBLE = '<INACCESSIBLE>'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def remove_non_ascii_characters(string):
    return ''.join([i if ord(i) < 128 else '' for i in string]).strip()

def parse_address(address):
    zipcode = re.findall(r' \d{5}', address)[0]
    address = address.replace(zipcode, '')
    city, state = address.split(',')
    return [
        remove_non_ascii_characters(item)
        for item in [city, state, zipcode]
    ]

def fetch_data():

    data = []

    base_link = 'https://www.softsurroundings.com/stores/all/'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    store_urls = [
        "https://www.softsurroundings.com" + a_tag['href']
        for a_tag in base.find(id="storeResults").find_all(class_="button thin")
    ]

    for store_url in store_urls:
        if "///" in store_url:
            continue
            
        req = session.get(store_url, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")

        location_name = base.h2.text.strip()

        address = list(base.find(class_='storeList').stripped_strings)
        street_address = address[0]
        city, state, zipcode = parse_address(address[1])
        state = re.findall(r'[A-Z]{2}', state)[0]
        phone = address[2]
        store_number = base.find(id='storeId')['value']

        hours_of_operation = " ".join(list(base.find(style="line-height:2.0em;margin-bottom:0.5em;").stripped_strings)).replace("\xa0"," ") \
            .replace("Now Open", '').replace("Now open", '') \
            .replace("!", '').replace("Store Hours:","").strip()

        try:
            hours_of_operation = hours_of_operation.split("order.")[1].strip()
        except:
            pass

        if not hours_of_operation:
            hours_of_operation = " ".join(list(base.find(class_="MsoNormal").stripped_strings)).replace("\xa0"," ") \
                .replace("Now Open", '').replace("Now open", '') \
                .replace("!", '').replace("Store Hours:","").strip()

        if 'Opening' in hours_of_operation: continue

        # Maps
        map_link = base.find(class_='storeList').a["href"]
        req = session.get(map_link, headers = HEADERS)
        maps = BeautifulSoup(req.text,"lxml")

        try:
            raw_gps = maps.find('meta', attrs={'itemprop': "image"})['content']
            lat = raw_gps[raw_gps.find("=")+1:raw_gps.find("%")].strip()
            lon = raw_gps[raw_gps.find("-"):raw_gps.find("&")].strip()
        except:
            lat = "<MISSING>"
            lon = "<MISSING>"

        data.append([
            BASE_URL,
            store_url,
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            store_number,
            phone,
            MISSING,
            lat,
            lon,
            hours_of_operation
        ])

    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
