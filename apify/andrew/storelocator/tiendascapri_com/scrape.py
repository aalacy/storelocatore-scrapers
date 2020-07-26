import csv
import re
import json
import time
from random import randint

from sgrequests import SgRequests
from bs4 import BeautifulSoup

BASE_URL = 'http://tiendascapri.com/tiendas'

user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
HEADERS = {'User-Agent' : user_agent}

session = SgRequests()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_driver():
    options = Options() 
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--window-size=1920,1080')
    return webdriver.Chrome('chromedriver', chrome_options=options)

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def remove_non_ascii_characters(string):
    return ''.join([i if ord(i) < 128 else ' ' for i in string]) \
        .replace('\r', '') \
        .replace('\n', '') \
        .strip()

def parse_address(address):
    address = [item.strip() for item in address.split(',')]
    if len(address) == 3:
        address = ['<MISSING>'] + address
    if len(address) == 5:
        address[:2] = [" ".join(address[:2])]
    address[2] = str(address[2])
    if not address[2].isdigit():
        address[:2] = [" ".join(address[:2])]
        street_address = address[0].replace('<MISSING>', '')
        state = address[2]
        zipcode = "".join([s for s in address[1].split() if s.isdigit()])
        city = address[1].replace(zipcode, '').strip()
        return street_address, city, zipcode, state
    return address[0], address[1], address[2], address[3]

def create_geo_hours_map(stores):
    geo_hours_map = {}
    keys = []
    duplicate_keys = []
    for store in stores:
        key = store['pin_city'].replace(' ', '') + store['pin_zip']
        # Ignore duplicate city+zipcode
        if key in duplicate_keys:
            continue
        if key in geo_hours_map:
            duplicate_keys.append(key)
            del geo_hours_map[key]
        geo = store['google_coords'][:2]
        hours = [
            remove_non_ascii_characters(re.sub(r'(<.*>)','', store['post_content']))
        ]
        geo_hours_map[key] = geo+hours
    return geo_hours_map

def fetch_data():

    driver = get_driver()
    time.sleep(2)

    data = []
    res = session.get(BASE_URL, headers = HEADERS)
    soup = BeautifulSoup(res.content, 'html.parser')
    stores = [
        [h4] + h4.find_next_siblings('p')
        for h4 in soup.select('div.column_attr > h4')
    ]
    geo = soup.select("div.mpfy-p-loading ~ script[type='text/javascript']")[1] \
        .text \
        .split('var inst = ')[-1] \
        .strip()
    geo = json.loads(re.findall(r'(\[.*\])', geo)[0])
    geo_hours_map = create_geo_hours_map(geo)
    for store in stores:
        location_name = re.sub(r'\B([A-Z])', r' \1', store[0].text)
        address = store[1].text
        phone = store[2].text
        if not re.match(r'\d{3}[-]{1}\d{3}[-]{1}\d{4}', phone):
            phone = '<MISSING>'
        street_address, city, zipcode, state = parse_address(address)
        geo_key = city.replace(' ', '')+zipcode
        try:
            lat, lon, hours = geo_hours_map[geo_key]
        except KeyError:
            lat, lon, hours = ['<INACCESSIBLE>']*3
        if street_address == "Plaza Guaynabo":
            lat = "18.3694131"
            lon = "-66.1107431"
        if lat == '<INACCESSIBLE>':
            map_link = store[-1].a['href']
            driver.get(map_link)
            time.sleep(8)

            try:
                map_link = driver.current_url
                at_pos = map_link.rfind("!3d")
                lat = map_link[at_pos+3:map_link.find("!", at_pos+3)].strip()
                lon = map_link[map_link.rfind("-"):].strip()
            except:
                pass

        data.append([
            'http://tiendascapri.com',
            BASE_URL,
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            '<MISSING>',
            phone,
            '<MISSING>',
            lat,
            lon,
            hours
        ])

    driver.close()
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()