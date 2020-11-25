import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('evenhotels_com')



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
    url = 'https://www.ihg.com/evenhotels/content/us/en/explore-hotels/main'
    r = session.get(url, headers=headers)
    Found = False
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'Discover More</a>' in line:
            lurl = line.split("href='")[1].split("'")[0]
            if 'https' in lurl:
                locs.append(lurl)
            else:
                locs.append('https:' + lurl)
    for loc in locs:
        logger.info(('Pulling Hotel %s...' % loc))
        r2 = session.get(loc, headers=headers)
        website = 'evenhotels.com'
        country = 'US'
        typ = 'Hotel'
        hours = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        store = ''
        phone = ''
        lat = ''
        lng = ''
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split('<')[0]
                city = line2.split('itemprop="addressLocality">')[1].split('<')[0]
                state = line2.split('<span itemprop="addressRegion">')[1].split('<')[0]
                zc = line2.split('"postalCode">')[1].split('<')[0]
            if 'itemprop="telephone"><a href="tel:+' in line2:
                phone = line2.split('itemprop="telephone"><a href="tel:+')[1].split('"')[0]
            if 'place:location:latitude"  content="' in line2:
                lat = line2.split('place:location:latitude"  content="')[1].split('"')[0]
            if 'place:location:longitude" content="' in line2:
                lng = line2.split('place:location:longitude" content="')[1].split('"')[0]
            if 'property="og:url"' in line2:
                store = line2.split('/hoteldetail')[0].rsplit('/',1)[1]
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
        if phone == '':
            phone = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
