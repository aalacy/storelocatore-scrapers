import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

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
    url = 'https://public.websteronline.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://public.websteronline.com/location/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        r2 = session.get(loc, headers=headers, verify=False)
        if r2.encoding is None: r2.encoding = 'utf-8'
        print(('Pulling Location %s...' % loc))
        website = 'public.websteronline.com'
        typ = ''
        store = ''
        add = ''
        zc = '<MISSING>'
        state = '<MISSING>'
        city = '<MISSING>'
        country = ''
        name = ''
        phone = '<MISSING>'
        hours = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        country = 'US'
        HFound = False
        PFound = False
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if HFound is False and 'Banking Center Hours</h2>' in line2:
                HFound = True
            if HFound and '</div>' in line2:
                HFound = False
            if HFound and 'Banking Center Hours</h2>' not in line2:
                hrs = line2.rsplit('<',1)[0].strip().replace('\t','').replace('<p>','').replace('<strong>','').replace('</strong>','')
                if hours == '<MISSING>':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '"entityBundle":"location","entityId":"' in line2:
                store = line2.split('"entityBundle":"location","entityId":"')[1].split('"')[0]
            if "<h1><span class='heading-small'>" in line2:
                typ = line2.split("Webster Bank's ")[1].split(' located')[0]
            if '</span></h1>' in line2:
                name = line2.split('<span>')[1].split('<')[0]
            if '<h2>Address &amp; Phone</h2>' in line2:
                next(lines)
                add = next(lines).split('<')[0].strip().replace('\t','')
            if '<span class="locality">' in line2:
                city = line2.split('<span class="locality">')[1].split('<')[0]
            if '<abbr class="region">' in line2:
                state = line2.split('<abbr class="region">')[1].split('<')[0]
            if '<span class="postal-code">' in line2:
                zc = line2.split('<span class="postal-code">')[1].split('<')[0]
            if '<a href="tel:' in line2 and PFound is False:
                PFound = True
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if "if(cur_latitude === ''" in line2:
                g = next(lines)
                lat = g.split('latitude=')[1].split('&')[0]
                lng = g.split('longitude=')[1].split('&')[0]
        if hours == '<MISSING>':
            hours = ''
        if add != '':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
