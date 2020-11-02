import csv
import re
import pdb
import requests
from lxml import etree
import json
from unidecode import unidecode
import us

base_url = 'https://www.boosterjuice.com'

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)
    return

def handle_missing(field):
    if field == None or (type(field) == type('x') and len(field.strip()) == 0):
        return '<MISSING>'
    else:
        field = unidecode(field).strip()
        return field if field else '<MISSING>'

def fetch_data():
    output_list = []
    url = "https://www.boosterjuice.com/WebServices/Booster.asmx/StoreLocations"
    session = requests.Session()
    request = session.get(url)
    store_list = json.loads(request.text)
    idx = 0
    for store in store_list:
        idx += 1
        output = []
        hours = store.get('hours')
        store_hours = []
        if len(hours) > 0:
            for x in hours:
                if x.get('isClosed') == True:
                    continue
                store_hours.append((x.get('day') or ' ') + ' ' + (x.get('open') or ' ') + ' ' + (x.get('close') or ' '))
        hours = '<MISSING>'
        if len(store_hours) > 0:
            hours = ', '.join(store_hours)
        country_code = '<MISSING>'
        if (len(re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', store.get('postalCode'))))==1:
            country_code = 'CA'
        elif us.states.lookup(store.get('province')):
            country_code = 'US'
        elif len(store.get('province').strip()) > 0 and len(store.get('postalCode').strip()) > 0:
            continue
        output.append(base_url)
        output.append('<MISSING>')
        output.append(handle_missing(store.get('name')))
        output.append(handle_missing(store.get('address')))
        output.append(handle_missing(store.get('city')))
        output.append(handle_missing(store.get('province')))
        output.append(handle_missing(store.get('postalCode')))
        output.append(handle_missing(country_code))
        output.append(handle_missing(str(store.get('number'))))
        output.append(handle_missing(store.get('phoneNumber')))
        output.append('<MISSING>')
        lat = '<MISSING>' if store.get('latitude') == 0 else str(store.get('latitude'))
        lng = '<MISSING>' if store.get('longitude') == 0 else str(store.get('longitude'))
        output.append(lat)
        output.append(lng)
        output.append(hours)
        output_list.append(output)
    return output_list
    
def scrape():
    data = fetch_data()
    write_output(data)

scrape()
