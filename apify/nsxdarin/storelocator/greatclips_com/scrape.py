import csv
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
    url = 'https://www.greatclips.com/sitemap.GreatClipsSalons.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'hreflang="en" href="https://salons.greatclips.com/us/' in line or 'hreflang="en" href="https://salons.greatclips.com/ca/' in line:
            lurl = line.split('hreflang="en" href="')[1].split('"')[0]
            if lurl.count('/') == 6:
                locs.append(lurl)
    for loc in locs:
        website = 'greatclips.com'
        typ = 'Salon'
        hours = ''
        if 'salons.greatclips.com/us/' in loc:
            country = 'US'
        if 'salons.greatclips.com/ca/' in loc:
            country = 'CA'
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        store = '<MISSING>'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode('utf-8'))
            if '<span class="LocationName-geo">' in line2:
                name = line2.split('<span class="LocationName-geo">')[1].split('<')[0]
                name = 'Great Clips ' + name
            if 'itemprop="streetAddress" content="' in line2:
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
            if 'class="c-address-city">' in line2:
                city = line2.split('class="c-address-city">')[1].split('<')[0].strip()
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0].strip()
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0].strip()
            if 'id="phone-main">' in line2:
                phone = line2.split('id="phone-main">')[1].split('<')[0]
            if 'itemprop="openingHours" content="' in line2:
                days = line2.split('itemprop="openingHours" content="')
                for day in days:
                    if '<table class="c-hours-details">' not in day:
                        hrs = day.split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
        if lat == '':
            lat = '<MISSING>'
        if lng == '':
            lng = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if ' ' in zc:
            country = 'CA'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
