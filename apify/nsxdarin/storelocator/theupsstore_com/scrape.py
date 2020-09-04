import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://locations.theupsstore.com/sitemap.xml'
    sms = []
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '/sitemap.xml.' in line:
            sms.append(line.split('>')[1].split('<')[0])
    for sm in sms:
        r2 = session.get(sm, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<loc>https://locations.theupsstore.com/' in line2:
                lurl = line2.split('>')[1].split('<')[0]
                count = lurl.count('/')
                if count == 5 and lurl not in locs:
                    locs.append(lurl)
    print(('Found %s Locations...' % (str(len(locs)))))
    for loc in locs:
        website = 'theupsstore.com'
        country = ''
        lat = ''
        lng = ''
        typ = 'UPS Store'
        store = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        hours = ''
        phone = ''
        zc = ''
        city = ''
        add = ''
        store2 = ''
        HFound = False
        NFound = False
        for line2 in lines:
            if NFound is False and '<span class="LocationName-geo">' in line2:
                NFound = True
                name = line2.split('<span class="LocationName-geo">')[1].split('<')[0]
            if 'class="OpenStatus-data" type="text/data">' in line2 and HFound is False:
                HFound = True
                hinfo = line2.split('class="OpenStatus-data" type="text/data">')[1].split('}</script>')[0].split('"day":"')
                for day in hinfo:
                    if 'hasIntervals' not in day:
                        dayname = day.split('"')[0]
                        if '"intervals":[]' in day:
                            hrs = 'Closed'
                        else:
                            hrs = day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                        if hours == '':
                            hours = dayname + ': ' + hrs
                        else:
                            hours = hours + '; ' + dayname + ': ' + hrs
            if '<meta itemprop="streetAddress" content="' in line2:
                add = line2.split('<meta itemprop="streetAddress" content="')[1].split('"')[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'itemprop="addressCountry">' in line2:
                country = line2.split('itemprop="addressCountry">')[1].split('<')[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
            if '<meta itemprop="addressLocality" content="' in line2:
                city = line2.split('<meta itemprop="addressLocality" content="')[1].split('"')[0]
            if 'Button--napMobile" href="tel:' in line2:
                phone = line2.split('Button--napMobile" href="tel:')[1].split('"')[0]
            if 'id="store_id" name="StoreID" value="' in line2:
                store = line2.split('id="store_id" name="StoreID" value="')[1].split('"')[0]
            if 'href="https://facebook.com/TheUPSStore' in line2:
                store2 = line2.split('href="https://facebook.com/TheUPSStore')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if store == '':
            store = store2
        if store == '':
            store = '<MISSING>'
        if add != '':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
