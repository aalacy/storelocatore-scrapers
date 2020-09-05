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
    url = 'https://locations.michaelkors.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://locations.michaelkors.com/canada/' in line or '<loc>https://locations.michaelkors.com/us/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            if lurl.count('/') == 6:
                locs.append(lurl)
    for loc in locs:
        #print('Pulling Location %s...' % loc)
        website = 'michaelkors.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        if '/canada/' in loc:
            country = 'CA'
        else:
            country = 'US'
        phone = ''
        lat = ''
        lng = ''
        hours = ''
        store = '<MISSING>'
        HFound = False
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<span class="Heading-sub Heading--pre">' in line2:
                typ = line2.split('<span class="Heading-sub Heading--pre">')[1].split('<')[0]
            if '"dimension4":"' in line2:
                add = line2.split('"dimension4":"')[1].split('"')[0]
                zc = line2.split('"dimension5":"')[1].split('"')[0]
                city = line2.split('"dimension3":"')[1].split('"')[0]
                state = line2.split('"dimension2":"')[1].split('"')[0]
            if '<span class="Heading-main">' in line2:
                name = line2.split('<span class="Heading-main">')[1].split('<')[0]
            if 'data-ya-track="phonecall">' in line2:
                phone = line2.split('data-ya-track="phonecall">')[1].split('<')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
            if HFound is False and "data-days='[{" in line2:
                HFound = True
                days = line2.split("data-days='[{")[1].split(']}]')[0].split('"day":"')
                for day in days:
                    if '"intervals"' in day:
                        if '"intervals":[]' in day:
                            hrs = day.split('"')[0] + ': Closed'
                        else:
                            try:
                                hrs = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                            except:
                                hrs = day.split('"')[0] + ': Closed'
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
