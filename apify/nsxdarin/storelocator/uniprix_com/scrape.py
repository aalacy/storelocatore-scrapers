import csv
from sgselenium import SgSelenium
from sgrequests import SgRequests

driver = SgSelenium().chrome()

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
    cities = []
    driver.get('https://www.uniprix.com/en/all-cities')
    lines = driver.page_source.split('\n')
    for linenum in range(0, len(lines)):
        linetext = lines[linenum]
        if '<a href="https://www.uniprix.com/en/stores/city/' in linetext:
            cities.append(lines[linenum].split('href="')[1].split('"')[0])
    for city in cities:
        driver.get(city)
        lines = driver.page_source.split('\n')
        for linenum in range(0, len(lines)):
            linetext = lines[linenum]
            if '<a href="https://www.uniprix.com/en/stores/' in linetext:
                lurl = lines[linenum].split('href="')[1].split('"')[0]
                if lurl not in locs:
                    locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        # print('Pulling Location %s...' % loc)
        r = session.get(loc, headers=headers)
        website = 'www.uniprix.com'
        typ = '<INACCESSIBLE>'
        store = '<MISSING>'
        add = ''
        zc = ''
        state = ''
        city = ''
        country = 'CA'
        name = ''
        phone = ''
        hours = ''
        lat = ''
        lng = ''
        lines = r.iter_lines(decode_unicode=True)
        for line2 in lines:
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if 'itemprop="streetAddress">' in line2:
                g = next(lines)
                h = next(lines)
                if '</a' in g:
                    add = g.split('</a')[0].strip().replace('\t','').replace('<br/>',' ')
                else:
                    add = h.split('</a')[0].strip().replace('\t','').replace('<br/>',' ')
            if 'itemprop="addressLocality">' in line2:
                g = next(lines)
                h = next(lines)
                if '<' in g:
                    city = g.strip().replace('\t','').split('  ')[0]
                    zc = g.strip().replace('\t','').split('  ')[0].split('<')[0]
                else:
                    city = h.strip().replace('\t','').split('  ')[0]
                    zc = h.strip().replace('\t','').split('  ')[0].split('<')[0]
                state = 'Quebec'
            if 'hollow_btn phone" href="tel:' in line2:
                phone = line2.split('hollow_btn phone" href="tel:')[1].split('"')[0]
            if 'data-lat="' in line2:
                lat = line2.split('data-lat="')[1].split('"')[0]
            if 'data-lng="' in line2:
                lng = line2.split('data-lng="')[1].split('"')[0]
            if 'datetime="' in line2:
                if hours == '':
                    hours = line2.split('datetime="')[1].split('"')[0]
                else:
                    hours = hours + '; ' + line2.split('datetime="')[1].split('"')[0]
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
