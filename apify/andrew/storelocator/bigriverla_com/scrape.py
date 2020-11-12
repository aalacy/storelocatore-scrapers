from sgrequests import SgRequests
from bs4 import BeautifulSoup
import csv
import re

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        # Body
        for row in data:
            writer.writerow(row)

def parse_address(address):
    _address = address[1:]
    street_address = _address[0].replace(',', '')
    city, _address = _address[1].split(',')
    state, zip_code = _address.split()
    return street_address, city, state, zip_code

def parse_geo(url):
    lon = re.findall(r'2d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    lat = re.findall(r'3d{1}(-?\d*.{1}\d*)!{1}', url)[0]
    return lat, lon

def fetch_data():
    data = []
    store_urls = []

    base_link = 'https://www.bigriverla.com/'

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36'
    HEADERS = {'User-Agent' : user_agent}

    session = SgRequests()
    req = session.get(base_link, headers = HEADERS)
    base = BeautifulSoup(req.text,"lxml")

    # Fetch store urls from location menu
    store_els = base.find(class_="sub-menu").find_all("a")
    for store_el in store_els:
        if "coming" not in store_el.text.lower():
            store_urls.append(store_el['href'])
    # Fetch data for each store url
    for store_url in store_urls:
        req = session.get(store_url, headers = HEADERS)
        base = BeautifulSoup(req.text,"lxml")
        # Fetch address/phone elements
        location_name = base.h1.text.strip()
        address_el = list(base.find(class_="wpb_text_column wpb_content_element").stripped_strings)
        # Parse address/phone elements
        street_address, city, state, zipcode = parse_address(address_el)
        phone = address_el[-1]
        # Regex match for store number in store name
        store_number = re.findall(r'#(\d+)', location_name)[0]
        location_type = ", ".join(list(base.find_all(class_="wpb_text_column wpb_content_element")[-1].stripped_strings)).encode("ascii", "replace").decode().replace("?","'")
        lat, lon = parse_geo(base.iframe['src'])
        data.append([
            'https://www.bigriverla.com/',
            store_url,
            location_name,
            street_address,
            city,
            state,
            zipcode,
            'US',
            store_number,
            phone,
            location_type,
            lat,
            lon,
            '<MISSING>'
        ])
    return data

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
