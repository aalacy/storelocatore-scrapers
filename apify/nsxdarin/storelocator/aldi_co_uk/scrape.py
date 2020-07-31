import csv
from sgrequests import SgRequests
import time
import re
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def get_json_data(html):
    re_get_json = re.compile('window\.dataLayer\.push\((.+?)\)')
    match = re.search(re_get_json, html)
    json_text = match.group(1)
    return json.loads(json_text)['seoData']


def get_geo_data(html):
    re_get_json = re.compile('<script class=\"js-store-finder-initial-state\" type=\"application/json\">\s\S?(.+?)</script>')
    match = re.search(re_get_json, html)
    json_text = match.group(1).strip()
    return json.loads(json_text)


def fetch_data():
    locs = []
    sm = ''
    url = 'https://www.aldi.co.uk/sitemap.xml'
    
    r = session.get(url, headers=headers)
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://www.aldi.co.uk/sitemap/store' in line:
            sm = line.split('<loc>')[1].split('<')[0]
    r = session.get(sm, headers=headers)
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://www.aldi.co.uk/store/' in line:
            locs.append(line.split('>')[1].split('<')[0])
    for loc in locs:
        time.sleep(3)
        print('Pulling Location %s ...' % loc)
        website = 'aldi.co.uk'
        store = loc.split('s-uk-')[1]
        typ = 'Store'
        hours = ''
        country = 'GB'
        name = ''
        state = ''
        city = ''
        add = ''
        zc = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        data = get_json_data(r2.text)
        name = data['name']
        try:
            hours = "; ".join(data['openingHours'])
        except:
            hours = '<MISSING>'
        city = data['address']['addressLocality']   
        state = '<MISSING>'
        add = data['address']['streetAddress']
        zc = data['address']['postalCode']

        geo_data = get_geo_data(r2.text)
        lat = geo_data['store']['latlng']['lat']
        lng = geo_data['store']['latlng']['lng']

        if hours == '':
            hours = '<MISSING>'
        phone = '<MISSING>'
    
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
