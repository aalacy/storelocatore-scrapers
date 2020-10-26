import csv
import urllib.request, urllib.error, urllib.parse
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
    allurls = []
    url = 'https://www.williams-sonoma.com/customer-service/store-locator.html?cm_type=gnav#'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    cty = ''
    for line in lines:
        if 'United States</h2>' in line:
            cty = 'US'
        if 'Canada</h2>' in line:
            cty = 'CA'
        if 'Mexico</h2>' in line:
            cty = 'MX'
        if '<a href="https://www.williams-sonoma.com/stores/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            outlet = 'N'
            g = next(lines)
            if 'outlet-store-icon' in g:
                outlet = 'Y'
            if cty == 'CA' or cty == 'US':
                if lurl not in allurls:
                    locs.append(lurl + '|' + cty + '|' + outlet)
                    allurls.append(lurl)
    for loc in locs:
        purl = loc.split('|')[0]
        country = loc.split('|')[1]
        typ = ''
        print(('Pulling Location %s...' % purl))
        website = 'williams-sonoma.com'
        hours = ''
        name = ''
        city = ''
        state = ''
        add = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(purl, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if "storeType: '" in line2:
                typ = line2.split("storeType: '")[1].split("'")[0]
            if 'class="store-name">' in line2:
                name = line2.split('class="store-name">')[1].split('<')[0]
            if 'class="store-address1">' in line2:
                add = line2.split('class="store-address1">')[1].split('<')[0]
            if 'class="store-city">' in line2:
                city = line2.split('class="store-city">')[1].split('<')[0]
            if 'class="store-state">' in line2:
                state = line2.split('class="store-state">')[1].split('<')[0]
            if 'class="store-zipcode">' in line2:
                zc = line2.split('class="store-zipcode">')[1].split('<')[0]
            if "lat:'" in line2:
                lat = line2.split("lat:'")[1].split("'")[0]
            if "lng:'" in line2:
                lng = line2.split("lng:'")[1].split("'")[0]
            if "{day: '" in line2:
                hrs = line2.split("{day: '")[1].split("'")[0] + ': ' + line2.split("hours: '")[1].split("'")[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '<p class="store-address2">' in line2:
                try:
                    add = add + ' ' + line2.split('<p class="store-address2">')[1].split('<')[0]
                except:
                    pass
            if "storeNumber: '" in line2:
                store = line2.split("storeNumber: '")[1].split("'")[0]
            if 'class="store-phone">' in line2:
                phone = line2.split('class="store-phone">')[1].split('<')[0]
        if hours == '':
            hours = '<MISSING>'
        if zc == '':
            zc = '<MISSING>'
        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
