import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.corkyskitchenandbakery.com/locations'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    website = 'corkyskitchenandbakery.com'
    typ = '<MISSING>'
    country = 'US'
    loc = '<MISSING>'
    store = '<MISSING>'
    hours = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    for line in r.iter_lines(decode_unicode=True):
        if '"@type":"Restaurant","' in line:
            items = line.split('"@type":"Restaurant","')
            for item in items:
                if '"streetAddress":"' in item:
                    add = item.split('"streetAddress":"')[1].split('"')[0]
                    phone = item.split('"telephone":"')[1].split('"')[0]
                    city = item.split('"addressLocality":"')[1].split('"')[0]
                    state = item.split('"addressRegion":"')[1].split('"')[0]
                    hours = item.split('"openingHours":["')[1].split(']')[0].replace('","','; ').replace('"','')
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    if '0' not in hours:
                        hours = '<MISSING>'
                    name = city
                    if '0000' in phone:
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
