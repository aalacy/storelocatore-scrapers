import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import time

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
    states = []
    Found = False
    url = 'https://www.libertytaxcanada.ca/office-directory/'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<h2>Provinces</h2>' in line:
            Found = True
        if Found and '<!-- FOOTER -->' in line:
            Found = False
        if Found and '-tax-preparation-locations.html">' in line:
            states.append('https://www.libertytaxcanada.ca' + line.split('href="')[1].split('"')[0])
    for state in states:
        time.sleep(5)
        print(('Pulling Province %s...' % state))
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'More detail</a>' in line2:
                locs.append('https://www.libertytaxcanada.ca' + line2.split('href="')[1].split('"')[0])
    for loc in locs:
        time.sleep(5)
        print(('Pulling Location %s...' % loc))
        website = 'libertytaxcanada.ca'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        country = 'CA'
        zc = ''
        phone = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        store = ''
        HFound = False
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<h1>' in line2:
                name = line2.split('<h1>')[1].split('<')[0]
            if 'streetAddress' in line2:
                add = line2.split('streetAddress')[1].split('>')[1].split('<')[0]
            if 'addressLocality' in line2:
                city = line2.split('addressLocality')[1].split('>')[1].split('<')[0]
            if 'addressRegion' in line2:
                state = line2.split('addressRegion')[1].split('>')[1].split('<')[0]
            if 'postalCode' in line2:
                zc = line2.split('postalCode')[1].split('>')[1].split('<')[0]
            if 'id=office-number' in line2:
                phone = line2.split('tel:')[1].split('"')[0]
            if 'OfficeId' in line2:
                store = line2.split('value=')[1].split(' ')[0].replace('"','').strip()
            if '<div class="office-hours-week' in line2 and hours == '':
                HFound = True
            if HFound and '</section>' in line2:
                HFound = False
            if HFound and '<span class="office-day-name">' in line2:
                day = line2.split('<span class="office-day-name">')[1].split('<')[0]
            if HFound and '<span class="office-day-hours">' in line2:
                hrs = day + ': ' + line2.split('<span class="office-day-hours">')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '<span itemprop="telephone" class="hidden">' in line2:
                phone = line2.split('<span itemprop="telephone" class="hidden">')[1].split('<')[0]
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        hours = hours.replace('\t','').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
