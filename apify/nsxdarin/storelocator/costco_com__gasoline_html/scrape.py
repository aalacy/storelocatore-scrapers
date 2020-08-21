import csv
from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt

session = SgRequests()

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

@retry(stop = stop_after_attempt(7))
def fetch_loc(loc):
    return session.get(loc, headers = headers)

def fetch_data():
    locs = []
    url = 'https://www.costco.com/sitemap_l_001.xml'
    r = fetch_loc(url)
    for raw_line in r.iter_lines():
        line = str(raw_line)
        if '<loc>https://www.costco.com/warehouse-locations/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        website = 'costco.com/gasoline.html'
        typ = 'Gas'
        hours = ''
        phone = ''
        add = ''
        name = ''
        city = ''
        zc = ''
        state = ''
        lat = ''
        lng = ''
        store = ''
        country = 'US'
        HFound = False
        IsGas = False
        r2 = fetch_loc(loc) 
        for line in r2.iter_lines(): 
            g = str(line)
            if 'Gas Hours</span>' in g:
                IsGas = True
                HFound = True
            if HFound and 'gas-price-section">' in g:
                HFound = False
            if HFound and '<time itemprop="openingHours" datetime="' in g:
                text = g.split('<time itemprop="openingHours" datetime="')[1].split('"')[0]
                if 'am' in text or 'pm' in text:
                    hrs = text.strip()
                    allhrs = day + ': ' + hrs
                else:
                    day = text.strip()
                    allhrs = ''
                if allhrs != '':
                    if hours == '':
                        hours = allhrs
                    else:
                        hours = hours + '; ' + allhrs
            if 'itemprop="latitude" content="' in g:
                lat = g.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in g:
                lng = g.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'data-identifier="' in g:
                store = g.split('data-identifier="')[1].split('"')[0]
            if '<h1' in g:
                name = g.split('<h1')[1].split('>')[1].split('<')[0].replace('&nbsp;',' ')
            if 'itemprop="streetAddress">' in g:
                add = g.split('itemprop="streetAddress">')[1].split('<')[0]
            if 'itemprop="addressLocality">' in g:
                city = g.split('itemprop="addressLocality">')[1].split('<')[0]
            if 'itemprop="addressRegion">' in g:
                state = g.split('itemprop="addressRegion">')[1].split('<')[0]
            if 'itemprop="postalCode">' in g:
                zc = g.split('itemprop="postalCode">')[1].split('<')[0]
            if phone == '' and 'itemprop="telephone">' in g:
                phone = g.split('itemprop="telephone">')[1].split('<')[0].strip().replace('\t','')
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if add != '' and IsGas is True:
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
