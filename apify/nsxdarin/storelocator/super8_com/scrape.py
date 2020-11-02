import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('super8_com')



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
    url = 'https://www.wyndhamhotels.com/en-ca/super-8/locations'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    Found = True
    for line in r.iter_lines(decode_unicode=True):
        if 'section-name headline-i">Asia</h3>' in line:
            Found = False
        if Found and 'overview">Super 8' in line:
            locs.append('https://www.wyndhamhotels.com' + line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'super8.com'
        typ = 'Restaurant'
        hours = '<MISSING>'
        typ = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        country = ''
        zc = ''
        phone = ''
        store = '<MISSING>'
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'siteID : "' in line2:
                store = line2.split('siteID : "')[1].split('"')[0]
            if name == '' and '"name":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
            if '"latitude":' in line2:
                lat = line2.split('"latitude":')[1].split(',')[0]
            if '"longitude":' in line2:
                lng = line2.split('"longitude":')[1].strip().replace('\r','').replace('\t','').replace('\n','')
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
            if '"@type":"' in line2 and typ == '':
                typ = line2.split('"@type":"')[1].split('"')[0]
            if '"addressLocality":"' in line2:
                city = line2.split('"addressLocality":"')[1].split('"')[0]
            if '"addressRegion":"' in line2:
                state = line2.split('"addressRegion":"')[1].split('"')[0]
            if '"postalCode":"' in line2:
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '"addressCountry":"' in line2:
                country = line2.split('"addressCountry":"')[1].split('"')[0]
                if country == 'Canada':
                    country = 'CA'
                if 'US' in country or 'United States' in country:
                    country = 'US'
            if '"telephone":"' in line2:
                phone = line2.split('"telephone":"')[1].split('"')[0]
        if phone == '':
            phone = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
