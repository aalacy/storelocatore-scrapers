import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.olivegarden.ca/ca-locations-sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        store = loc.rsplit('/',1)[1]
        website = 'olivegarden.ca'
        country = 'CA'
        typ = 'Restaurant'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' Italian')[0]
            if 'id="restAddress" value="' in line2:
                add = line2.split('id="restAddress" value="')[1].split(',')[0]
                city = line2.split('id="restAddress" value="')[1].split(',')[1]
                state = line2.split('id="restAddress" value="')[1].split(',')[2]
                zc = line2.split('id="restAddress" value="')[1].split(',')[3].split('"')[0]
            if ',"name":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"longitude":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                hours = line2.split('"openingHours":["')[1].split(']')[0].replace('","','; ').replace('"','')
                if phone == '':
                    phone = '<MISSING>'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
