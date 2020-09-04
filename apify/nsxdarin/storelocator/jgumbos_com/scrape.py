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
    coords = []
    url = 'https://www.jgumbos.com/Locations'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '"locations":[' in line:
            items = line.split('{"title":"')
            for item in items:
                if '"coordsOrAddress":"' in item:
                    lat = item.split('"coordsOrAddress":"')[1].split(',')[0]
                    lng = item.split('"coordsOrAddress":"')[1].split(',')[1].split('"')[0].strip()
                    website = 'jgumbos.com'
                    name = item.split('"')[0]
                    store = item.split(',"id":')[1].split('}')[0]
                    add = item.split('"street":"')[1].split('"')[0].strip()
                    city = item.split('"city":"')[1].split('"')[0].strip()
                    state = item.split('"state":"')[1].split('"')[0].strip()
                    country = 'US'
                    zc = item.split('"zip":"')[1].split('"')[0]
                    loc = '<MISSING>'
                    phone = item.split('"phone":"')[1].split('"')[0]
                    typ = '<MISSING>'
                    hours = ''
                    days = item.split('"storeLocationHours":[')[1].split(']')[0].split('"daysSummary":"')
                    for day in days:
                        if '"hoursSummary":"' in day:
                            hrs = day.split('"')[0] + ': ' + day.split('"hoursSummary":"')[1].split('"')[0]
                            if hours == '':
                                hours = hrs
                            else:
                                hours = hours + '; ' + hrs
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
