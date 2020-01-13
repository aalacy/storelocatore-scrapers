import csv
import urllib2
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
    locs = []
    url = 'https://www.bestwestern.com/etc/seo/bestwestern/hotels.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.bestwestern.com/en_US/book/' in line and 'https://www.bestwestern.com/en_US/book/hotels-in-' not in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'bestwestern.com'
        typ = '<MISSING>'
        hours = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        store = loc.split('/propertyCode.')[1].split('.')[0]
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(loc, headers=headers)
        try:
            for line2 in r2.iter_lines():
                if '&#34;street1&#34;:&#34;' in line2:
                    add = line2.split('&#34;street1&#34;:&#34;')[1].split('&#34')[0]
                    city = line2.split('&#34;city&#34;:&#34;')[1].split('&#34')[0]
                    state = line2.split('&#34;state&#34;:&#34;')[1].split('&#34')[0]
                    country = line2.split('&#34;country&#34;:&#34;')[1].split('&#34')[0]
                    zc = line2.split('&#34;postalcode&#34;:&#34;')[1].split('&#34')[0]
                    phone = line2.split('&#34;phoneNumber&#34;:&#34;')[1].split('&#34')[0]
                    lat = line2.split('&#34;,&#34;latitude&#34;:&#34;')[1].split('&#34')[0]
                    lng = line2.split('&#34;longitude&#34;:&#34;')[1].split('&#34')[0]
                    name = line2.split('&#34;name&#34;:&#34;')[1].split('&#34')[0]
                    if 'United States' in country:
                        country = 'US'
                    if 'Canada' in country:
                        country = 'CA'
            if country == 'US' or country == 'CA':
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        except:
            pass

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
