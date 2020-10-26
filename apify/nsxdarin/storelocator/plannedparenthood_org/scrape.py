import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import unidecode

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'accept': 'application/json',
           'x-requested-with': 'XMLHttpRequest'
           }

headers2 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def sanitize(s):
    return unidecode.unidecode(s)

def fetch_data():
    locs = []
    url = 'https://www.plannedparenthood.org/abortion-access/_health_centres'
    stores = session.get(url, headers=headers).json()['response']['facilities']
    for store in stores:
        hours = ''
        loc = 'https://www.plannedparenthood.org' + store["absolute_url"]
        store_number = store['pk']
        name = sanitize(store['name']) 
        typ = '<MISSING>'
        website = 'plannedparenthood.org'
        location = store['location']
        lng = location['lon_lat'].get('lng', '<MISSING>') 
        lat = location['lon_lat'].get('lat', '<MISSING>')
        add = sanitize(location.get("address", '<MISSING>'))
        city = sanitize(location.get("city", '<MISSING>'))
        state = sanitize(location.get("state", '<MISSING>'))
        zc = sanitize(location.get('zipcode', '<MISSING>'))
        phone = sanitize(store['phone'].get('display', '<MISSING>'))
        country = 'US'
        print(('Pulling Location %s...' % loc))
        r2 = session.get(loc, headers=headers2)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"openingHours": ["' in line2:
                hours = line2.split('"openingHours": ["')[1].split(']')[0].replace('", "','; ').replace('"','')
        if hours == '':
            hours = '<MISSING>'
        fields = [website, loc, name, add, city, state, zc, country, store_number, phone, typ, lat, lng, hours]
        yield fields

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
