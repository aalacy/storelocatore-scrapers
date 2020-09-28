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
    url = 'https://www.phoenixrehab.com/locations/'
    locs = []
    website = 'phoenixrehab.com'
    typ = '<MISSING>'
    store = '<MISSING>'
    country = 'US'
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<li class="light-16"><a href="' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if '/ohio' not in lurl:
                locs.append(lurl)
    print(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        lat = ''
        lng = ''
        hours = ''
        zc = ''
        phone = ''
        print(('Pulling Location %s...' % loc))
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '{"@type":"Organization' in line2:
                name = line2.rsplit('"name":"',1)[1].split('"')[0]
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split('<')[0]
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
            if 'itemprop="telephone" content="' in line2:
                phone = line2.split('itemprop="telephone" content="')[1].split('"')[0].encode('utf-8')
            if '<div class="map--id">Store #' in line2:
                store = line2.split('<div class="map--id">Store #')[1].split('<')[0]
            if 'map_marker.png' in line2:
                lat = line2.split('map_marker.png')[1].split('%7C')[1].split('%')[0]
                lng = line2.split('map_marker.png')[1].split('%2C')[1].split('&')[0]
            if 'data-loc-tt="{&quot;' in line2:
                hours = line2.split('data-loc-tt="{&quot;')[1].split('}">')[0]
                hours = hours.replace(':{&quot;open&quot;:false,&quot;close&quot;:false}','Closed')
                hours = hours.replace('},&quot;','; ').replace('&quot;',' ').strip().replace('  ',' ')
                hours = hours.replace(' , close : ','-').replace('{ open : ',' ')
                hours = hours.replace(' :',':').replace(' ;',';').replace(', sunday','; sunday')
        if 'smithfield' in city.lower():
            lat = '36.9579509'
            lng = '-76.6052515'
        if 'chambersburg' in city.lower():
            lat = '39.9284938'
            lng = '-77.6305067'
        if add != '':
            if lat == '':
                lat = '<MISSING>'
                lng = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
    url = 'https://www.phoenixrehab.com/ohio/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    name = ''
    hours = '<MISSING>'
    print('Pulling OH Locations...')
    for line in lines:
        if '<h3 class="clinic-title">' in line:
            if name != '':
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            name = line.split('<h3 class="clinic-title">')[1].split('<')[0]
            loc = '<MISSING>'
            hours = '<MISSING>'
        if '<p class="clinic-address">' in line:
            g = next(lines)
            h = next(lines)
            add = g.split('<')[0].strip().replace('\t','')
            csz = h.strip().replace('\t','').replace('\r','').replace('\n','')
            if '<' in csz:
                csz = csz.split('<')[0]
            csz = csz.replace(' ',' ')
            city = csz.split(',')[0]
            if 'Warren' in name:
                city = 'Cortland'
                zc = '44410'
            else:
                zc = csz.rsplit(' ',1)[1]
            state = 'OH'
        if '<a href="tel:+1-' in line:
            phone = line.split('<a href="tel:+1-')[1].split('"')[0]
            lat = '<MISSING>'
            lng = '<MISSING>'
        if '<a class="website-link" href="' in line:
            loc = line.split('<a class="website-link" href="')[1].split('"')[0]
            r2 = session.get(loc, headers=headers)
            if r2.encoding is None: r2.encoding = 'utf-8'
            hours = ''
            for line2 in r2.iter_lines(decode_unicode=True):
                if 'HOURS: </strong>' in line2:
                    hours = line2.split('HOURS: </strong>')[1].split('</p>')[0].replace('<br />','; ').replace('&#8211;','-')
        if '</main><!-- #main -->' in line:
            if lat == '':
                lat = '<MISSING>'
                lng = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
