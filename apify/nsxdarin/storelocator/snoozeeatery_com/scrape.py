import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
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

def fetch_data():
    url = 'https://snoozeeatery.com/locations-sitemap.xml'
    states = []
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://www.snoozeeatery.com/locations/' in line and 'post_id' not in line:
            states.append(line.split('<loc>https://www.snoozeeatery.com/locations/')[1].split('/')[0])
    for state in states:
        print(('Pulling State %s...' % state))
        surl = 'https://snoozeeatery.com/wp-json/koa/v1/entry/' + state
        r2 = session.get(surl, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '"branches":[' in line2:
                items = line2.split('"branches":[')
                for item in items:
                    if '"date_gmt":"' not in item:
                        bids = item.split(']')[0].split(',')
                        for bid in bids:
                            locs.append(bid)
    print(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        name = 'Snooze Eatery'
        print(('Pulling Location %s...' % loc))
        website = 'snoozeeatery.com'
        typ = 'Restaurant'
        lurl = 'https://snoozeeatery.com/wp-json/koa/v1/entry/' + loc
        r2 = session.get(lurl, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '{"id":' in line2 and 'Coming Soon' not in line2:
                name = line2.split('"title":{"rendered":"')[1].split('"')[0]
                store = line2.split('{"id":')[1].split(',')[0]
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                addinfo = line2.split('"address":{"title":"')[1].split('"')[0]
                hours = line2.split('"hours":"')[1].split('"')[0]
                try:
                    phone = line2.split('"phone_number":"')[1].split('"')[0]
                except:
                    phone = '<MISSING>'
                purl = line2.split('"link":"')[1].split('"')[0].replace('\\','')
                if addinfo.count(',') == 3:
                    add = addinfo.split(',')[0] + ' ' + addinfo.split(',')[1]
                    city = addinfo.split(',')[2].strip()
                    state = addinfo.split(',')[3].strip().split(' ')[0]
                    zc = addinfo.split(',')[3].strip().split(' ')[1]
                    add = add.strip().replace('  ',' ')
                else:
                    add = addinfo.split(',')[0]
                    city = addinfo.split(',')[1].strip()
                    state = addinfo.split(',')[2].strip().split(' ')[0]
                    zc = addinfo.split(',')[2].strip().split(' ')[1]
                    add = add.strip().replace('  ',' ')
        country = 'US'
        if 'Delivery - ' in hours:
            hours = hours.split('Delivery - ')[1]
        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
