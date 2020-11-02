import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('fantasticsams_com')



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
    canada = ['SK','ON','BC','PE','PEI','NB','NL','NS','YT','AB','MB','QC']
    url = 'https://www.fantasticsams.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>http://fantasticsams.com/about/regions/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            if lurl.count('/') == 6:
                locs.append(lurl)
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'fantasticsams.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        lat = ''
        lng = ''
        store = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        phone = ''
        CS = False
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'Coming Soon' in line2:
                CS = True
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if 'property="og:latitude" content="' in line2:
                lat = line2.split('property="og:latitude" content="')[1].split('"')[0]
            if 'property="og:longitude" content="' in line2:
                lng = line2.split('property="og:longitude" content="')[1].split('"')[0]
            if 'property="og:phone_number" content="' in line2:
                phone = line2.split('property="og:phone_number" content="')[1].split('"')[0]
            if '<div class="salon-address-thoroughfare">' in line2:
                add = line2.split('<div class="salon-address-thoroughfare">')[1].split('<')[0]
            if 'class="salon-address-premise">' in line2:
                add = add + ' ' + line2.split('class="salon-address-premise">')[1].split('<')[0]
                add = add.strip()
            if '"salon-address-city-state-zip">' in line2:
                city = line2.split('"salon-address-city-state-zip">')[1].split(',')[0]
                state = line2.split('"salon-address-city-state-zip">')[1].split(',')[1].strip().split(' ')[0]
                zc = line2.split('"salon-address-city-state-zip">')[1].split(',')[1].strip().split(' ',1)[1].split('<')[0]
                country = 'US'
                store = '<MISSING>'
            if '<span class="oh-display-label" style="width: 3em;">' in line2:
                days = line2.split('<span class="oh-display-label" style="width: 3em;">')
                for day in days:
                    if 'field-salon-hours">' not in day:
                        if hours == '':
                            hours = day.split('<')[0] + day.split('<div span class="oh-display')[1].split('">')[1].split('<')[0]
                        else:
                            hours = hours + '; ' + day.split('<')[0] + day.split('<div span class="oh-display')[1].split('">')[1].split('<')[0]
        if hours == '':
            hours = '<MISSING>'
        if lat == '':
            lat = '<MISSING>'
            lng = '<MISSING>'
        if state in canada:
            country = 'CA'
        if add != '' and CS is False:
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
