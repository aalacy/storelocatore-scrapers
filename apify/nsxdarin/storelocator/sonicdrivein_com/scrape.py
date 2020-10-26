import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import gzip
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('sonicdrivein_com')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w', encoding='utf-8') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://locations.sonicdrivein.com/sitemap/sitemap_index.xml'
    locs = []
    sitemaps = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://locations.sonicdrivein.com/sitemap/sitemap' in line:
            sitemaps.append(line.split('<loc>')[1].split('<')[0])
    for sm in sitemaps:
        smurl = sm
        with open('branches.xml.gz','wb') as f:
            f.write(urllib.request.urlopen(smurl).read())
            f.close()
            with gzip.open('branches.xml.gz', 'rt') as f:
                for line in f:
                    if '<loc>https://locations.sonicdrivein.com/' in line and '.html' in line:
                        lurl = line.split('<loc>')[1].split('<')[0]
                        if lurl not in locs:
                            locs.append(lurl)
        logger.info('%s Locations Found...' % str(len(locs)))
    for loc in locs:
        url = loc
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        phone = ''
        hours = ''
        lat = ''
        lng = ''
        store = ''
        name = 'Sonic Drive-In'
        website = 'sonicdrivein.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<div class="map-list-item-wrap" data-fid="' in line2:
                store = line2.split('<div class="map-list-item-wrap" data-fid="')[1].split('"')[0]
            #if '<span class="stores-nearby-text">' in line2:
                #name = line2.split('<span class="stores-nearby-text">')[1].split('<')[0]
            if '"latitude": "' in line2:
                lat = line2.split('"latitude": "')[1].split('"')[0]
            if '"longitude": "' in line2:
                lng = line2.split('"longitude": "')[1].split('"')[0]
            if '"streetAddress": "' in line2:
                add = line2.split('"streetAddress": "')[1].split('"')[0].strip()
            if '"addressLocality": "' in line2:
                city = line2.split('"addressLocality": "')[1].split('"')[0]
            if '"addressRegion": "' in line2:
                state = line2.split('"addressRegion": "')[1].split('"')[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if '"telephone": "' in line2:
                phone = line2.split('"telephone": "')[1].split('"')[0].strip()
            if '"openingHours": "' in line2:
                hours = line2.split('"openingHours": "')[1].split('"')[0].strip()
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
