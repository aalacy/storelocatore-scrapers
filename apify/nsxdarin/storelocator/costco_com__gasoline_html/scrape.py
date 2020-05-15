import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)


def fetch_data():
    locs = []
    url = 'https://www.costco.com/sitemap_l_001.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.costco.com/warehouse-locations/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'costco.com/gasoline.html'
        typ = 'Gas'
        hours = ''
        phone = ''
        add = ''
        city = ''
        zc = ''
        state = ''
        lat = ''
        lng = ''
        store = ''
        country = 'US'
        HFound = False
        IsGas = False
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if 'Gas Hours</span>' in line2:
                IsGas = True
                HFound = True
            if HFound and 'gas-price-section">' in line2:
                HFound = False
            if HFound and '<time itemprop="openingHours" datetime="' in line2:
                text = line2.split('<time itemprop="openingHours" datetime="')[
                    1].split('"')[0]
                if 'am' in text or 'pm' in text:
                    hrs = text.strip()
                    allhrs = day + ': ' + hrs
                else:
                    day = text.strip()
                    allhrs = ''
                if allhrs != '':
                    if hours == '':
                        hours = allhrs
                    else:
                        hours = hours + '; ' + allhrs
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[
                    1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[
                    1].split('"')[0]
            if 'data-identifier="' in line2:
                store = line2.split('data-identifier="')[1].split('"')[0]
            if '<h1 itemprop="name">' in line2:
                name = line2.split('<h1 itemprop="name">')[1].split('<')[
                    0].replace('&nbsp;', ' ')
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split('<')[0]
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[
                    1].split('<')[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[
                    1].split('<')[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
            if phone == '' and 'itemprop="telephone">' in line2:
                phone = line2.split('itemprop="telephone">')[1].split('<')[
                    0].strip().replace('\t', '')
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if add != '' and IsGas is True:
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
