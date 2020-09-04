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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.hungryhowies.com/locations'
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'href=\\u0022\\/store\\/' in line:
            items = line.split('href=\\u0022\\/store\\/')
            for item in items:
                if 'jQuery.extend(Drupal.settings' not in item:
                    loc = item.split('\\u0022')[0]
                    lurl = 'https://www.hungryhowies.com/store/' + loc
                    if lurl not in locs:
                        locs.append(lurl)
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        country = 'US'
        website = 'hungryhowies.com'
        typ = 'Restaurant'
        hours = ''
        for line2 in lines:
            if '"og:title" content="Hungry Howie&#039;s' in line2:
                name = "Hungry Howie's " + line2.split('"og:title" content="Hungry Howie&#039;s')[1].split('"')[0].strip()
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split(',"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                lat = line2.split(',"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if '<dt class="day">' in line2:
                items = line2.split('<dt class="day">')
                for item in items:
                    if '<dd class="time">' in item:
                        if hours == '':
                            hours = item.split('<')[0] + ' ' + item.split('<dd class="time">')[1].split('<')[0]
                        else:
                            hours = hours + '; ' + item.split('<')[0] + ' ' + item.split('<dd class="time">')[1].split('<')[0]
        if hours == '':
            hours = '<MISSING>'
        if lat == '':
            lat = '<MISSING>'
        if lng == '':
            lng = '<MISSING>'
        store = name.split('#')[1]
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
