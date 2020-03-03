import csv
import urllib2
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
    url = 'https://www.jiffylube.com/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<ns1:loc>https://www.jiffylube.com/locations/' in line:
            lurl = line.split('>')[1].split('<')[0]
            count = lurl.count('/')
            if count == 6:
                locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'jiffylube.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        store = loc.rsplit('/',1)[1]
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<meta itemprop="name" content="' in line2:
                name = line2.split('<meta itemprop="name" content="')[1].split('"')[0]
                if ' |' in name:
                    name = name.split(' |')[0]
            if '<span itemprop="streetAddress">' in line2:
                add = line2.split('<span itemprop="streetAddress">')[1].split('<')[0]
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split('<')[0]
            if '<span itemprop="addressRegion">' in line2:
                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
            if '<span itemprop="postalCode">' in line2:
                zc = line2.split('<span itemprop="postalCode">')[1].split('<')[0]
            if '<span itemprop="telephone" content="' in line2:
                phone = line2.split('<span itemprop="telephone" content="')[1].split('"')[0].replace('+','')
            if '<staticmap lat="' in line2:
                lat = line2.split('<staticmap lat="')[1].split('"')[0]
                lng = line2.split('lng="')[1].split('"')[0]
            if '<full-hours hours="' in line2:
                days = line2.split(';name&quot;:&quot;')
                for day in days:
                    if 'time_open&quot;:&quot;' in day:
                        dname = day.split('&')[0]
                        oh = day.split('time_open&quot;:&quot;')[1].split('&')[0]
                        ch = day.split('time_close&quot;:&quot;')[1].split('&')[0]
                        hrs = dname + ': ' + oh + '-' + ch
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
