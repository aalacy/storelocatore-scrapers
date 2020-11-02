import csv
from sgrequests import SgRequests
import time
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('pnc_com')



headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-frame-options': 'ALLOW-FROM https://www.apply2.pnc.com/',
           'x-xss-protection': '1; mode=block',
           'x-ua-compatible': 'IE=Edge',
           'strict-transport-security': 'max-age=31536000',
           'authority': 'apps.pnc.com',
           'method': 'GET',
           'scheme': 'https',
           'accept': 'application/json, text/plain, */*',
           'x-app-key': 'pyHnMuBXUM1p4AovfkjYraAJp6',
           'content-encoding': 'gzip'
           }

headers2 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://apps.pnc.com/locator-api/locator/api/v1/locator/browse?t=1578513813794'
    session = SgRequests()
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    locs = []
    for line in [str(x) for x in r.iter_lines(decode_unicode=True)]:
        if '"externalId" : "' in line:
            lid = line.split('" : "')[1].split('"')[0]
            locs.append(lid)
    logger.info(('Found %s Locations...' % str(len(locs))))
    i = 0
    for loc in locs:
        i += 1
        if i % 30 == 0:
            session = SgRequests()
        lurl = 'https://apps.pnc.com/locator-api/locator/api/v2/location/' + loc
        logger.info(('Pulling Location %s...' % loc))
        r2 = session.get(lurl, headers=headers2)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = (str(x) for x in r2.iter_lines(decode_unicode=True))
        website = 'pnc.com'
        HFound = False
        hours = ''
        TypFound = False
        for line2 in lines:
            if '"locationName" : "' in line2:
                name = line2.split('"locationName" : "')[1].split('"')[0]
            if '"locationTypeDesc" : "' in line2 and TypFound is False:
                TypFound = True
                typ = line2.split('"locationTypeDesc" : "')[1].split('"')[0]
                store = loc
            if '"address1" : "' in line2:
                add = line2.split('"address1" : "')[1].split('"')[0]
            if '"address2" : "' in line2:
                add = add + ' ' + line2.split('"address2" : "')[1].split('"')[0]
            if '"city" : "' in line2:
                city = line2.split('"city" : "')[1].split('"')[0]
            if '"state" : "' in line2:
                state = line2.split('"state" : "')[1].split('"')[0]
            if '"zip" : "' in line2:
                zc = line2.split('"zip" : "')[1].split('"')[0]
            if '"latitude" : ' in line2:
                lat = line2.split('"latitude" : ')[1].split(',')[0]
            if '"longitude" : ' in line2:
                lng = line2.split('"longitude" : ')[1].split(',')[0]
            if '"contactDescriptionDB" : "External Phone",' in line2:
                phone = next(lines).split(' : "')[1].split('"')[0]
            if '"serviceNameDB" : "Lobby Hours"' in line2:
                HFound = True
            if HFound and '"hoursByDayIndex"' in line2:
                HFound = False
            if HFound and 'day"' in line2:
                day = line2.split('"')[1]
                g = next(lines)
                h = next(lines)
                if 'null' in g:
                    hrs = 'Closed'
                else:
                    hrs = g.split('"')[3] + '-' + h.split('"')[3]
                if hours == '':
                    hours = day + ': ' + hrs
                else:
                    hours = hours + '; ' + day + ': ' + hrs
        country = 'US'
        purl = 'https://apps.pnc.com/locator/#/result-details/' + loc
        if hours == '':
            hours = '<MISSING>'
        purl = purl + '/' + name.replace('#','').replace(' ','-').lower()
        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
