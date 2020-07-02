import csv
import urllib2
from sgrequests import SgRequests

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.onehourheatandair.com/locations/?CallAjax=GetLocations'
    sms = []
    locs = []
    payload = {'CallAjax': 'GetLocations'}
    r = session.post(url, headers=headers, data=payload)
    for line in r.iter_lines():
        if '"Path":"' in line:
            items = line.split('"Path":"')
            for item in items:
                if '"ExternalDomain":' in item:
                    locs.append('https://www.onehourheatandair.com' + item.split('"')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'onehourheatandair.com'
        name = ''
        country = 'US'
        lat = '<MISSING>'
        lng = '<MISSING>'
        typ = 'Location'
        store = '<MISSING>'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        hours = '<MISSING>'
        phone = '<MISSING>'
        zc = '<MISSING>'
        city = '<MISSING>'
        state = '<MISSING>'
        add = '<MISSING>'
        for line2 in lines:
            if '<span itemprop="streetAddress">' in line2:
                g = next(lines)
                add = g.replace('\r','').replace('\t','').replace('\n','').strip()
            if '<span itemprop="postalCode">' in line2:
                zc = line2.split('<span itemprop="postalCode">')[1].split('<')[0]
            if '<title>' in line2:
                name = line2.split('>')[1].split(' |')[0]
            if '<span class="flex-middle margin-right-tiny">' in line2:
                city = line2.split('<span class="flex-middle margin-right-tiny">')[1].split(',')[0]
                state = line2.split('<span class="flex-middle margin-right-tiny">')[1].split('<')[0].rsplit(' ',1)[1]
            if '<a class="phone-link phone-number-style text-color" href="tel:' in line2:
                phone = line2.split('<a class="phone-link phone-number-style text-color" href="tel:')[1].split('"')[0]
        if name != '':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
