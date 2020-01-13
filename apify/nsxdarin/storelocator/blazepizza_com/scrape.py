import csv
import urllib2
import re
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
    url = 'https://hq.blazepizza.com/locations/birmingham-al-7th-ave/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'mapData =' in line:
            items = line.split('{"id":"')
            for item in items:
                if '"coming_soon":false' in item:
                    website = 'blazepizza.com'
                    typ = 'Restaurant'
                    hours = item.split('"hours":"')[1].split('"')[0]
                    cleanr = re.compile('<.*?>')
                    hours = re.sub(cleanr, '', hours)
                    name = item.split('"title":"')[1].split('"')[0]
                    city = item.split(',"city":"')[1].split('"')[0]
                    add = item.split(',"address":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    country = item.split('"country":"')[1].split('"')[0]
                    zc = item.split('"zip":"')[1].split('"')[0]
                    store = item.split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lon":"')[1].split('"')[0]
                    loc = 'https://hq.blazepizza.com/locations/' + item.split('"slug":"')[1].split('"')[0]
                    if hours == '':
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    if zc == '':
                        zc = '<MISSING>'
                    if country == 'Canada':
                        country = 'CA'
                    hours = hours.replace('\u2013','-').replace('&ndash;','-').replace('\\r','').replace('\\n','').replace('\\t','')
                    hours = hours.replace('\u00a0',' ').replace('am','am ').replace('pm','pm ').replace('  ',' ').strip()
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
