import csv
from sgrequests import SgRequests
from bs4 import BeautifulSoup
import json
import re

from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name='hallmark.com')

session = SgRequests()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # conn = http.client.HTTPSConnection("maps.hallmark.com")
    base_url = 'https://www.hallmark.com'
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.97 Safari/537.36",
        # 'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        # 'cache-control': "no-cache",
        # 'postman-token': "13913a57-e466-50b2-ee2b-c6d50ead7e1f"
    }

    data = []
    addresses = []

    r = session.get("https://maps.hallmark.com/api/getAsyncLocations?template=search&level=search&radius=10000&search=10010&limit=5000",headers=headers).json()

    log.info('Getting ' + str(len(r['markers'])) + " links..(Approx. 1hr..)")
    for x in r['markers']:
        soup = BeautifulSoup(x['info'], "lxml")
        locator_domain = base_url
        div_data = json.loads(soup.text)
        location_name = div_data['location_name'].split("-Curbside")[0].strip()
        street_address = div_data['address_1']
        city = div_data['city']
        state = div_data['region']
        zipp = div_data['post_code']
        country_code = div_data['country']
        phone = div_data['local_phone']
        store_number = x['locationId']
        location_type = '<MISSING>'
        latitude = x['lat']
        longitude = x['lng']

        page_url = div_data['url']

        r1 = session.get(page_url,headers=headers)
        soup1 = BeautifulSoup(r1.text, "lxml")

        hours_of_operation = ''
        if soup1.find('div', {'class': 'hours'}) != None:
            sentence = soup1.find(
                'div', {'class': 'hours'}).text.strip()
            pattern = re.compile(r'\s+')
            hours_of_operation = re.sub(pattern, ' ', sentence)

        if street_address in addresses:
            continue
        addresses.append(street_address)
        
        store = []
        store.append(locator_domain if locator_domain else '<MISSING>')
        store.append(location_name if location_name else '<MISSING>')
        store.append(street_address if street_address else '<MISSING>')
        store.append(city if city else '<MISSING>')
        store.append(state if state else '<MISSING>')
        store.append(zipp if zipp else '<MISSING>')
        store.append(country_code if country_code else '<MISSING>')
        store.append(store_number if store_number else '<MISSING>')
        store.append(phone if phone else '<MISSING>')
        store.append(location_type if location_type else '<MISSING>')
        store.append(latitude if latitude else '<MISSING>')
        store.append(longitude if longitude else '<MISSING>')
        store.append(
            hours_of_operation if hours_of_operation else '<MISSING>')
        store.append(page_url if page_url else '<MISSING>')
        data.append(store)

    return data

def scrape():
    data = fetch_data()
    write_output(data)


scrape()
