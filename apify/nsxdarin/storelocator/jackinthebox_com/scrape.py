import csv
import urllib2
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://locations.jackinthebox.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'hreflang="en" href="' in line:
            lurl = line.split('hreflang="en" href="')[1].split('"')[0]
            if lurl.count('/') >= 6:
                locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = ''
        lat = ''
        lng = ''
        hours = ''
        zc = ''
        phone = '<MISSING>'
        website = 'jackinthebox.com'
        typ = 'Restaurant'
        Found = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '{"ids":' in line2:
                store = line2.split('{"ids":')[1].split(',')[0]
            if "'dimension4', '" in line2:
                name = line2.split("'dimension4', '")[1].split("'")[0]
            if Found is False and '<span class="c-address-street-1">' in line2:
                Found = True
                add = line2.split('<span class="c-address-street-1">')[1].split('<')[0]
                city = line2.split('<span class="c-address-city">')[1].split('<')[0]
                try:
                    state = line2.split('class="c-address-state" itemprop="addressRegion">')[1].split('<')[0]
                except:
                    state = '<MISSING>'
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
                days = line2.split('itemprop="openingHours" content="')
                for day in days:
                    if '<noscript><iframe src="' not in day:
                        if hours == '':
                            hours = day.split('"')[0]
                        else:
                            hours = hours + '; ' + day.split('"')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
        country = 'US'
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if add != '' or state != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
