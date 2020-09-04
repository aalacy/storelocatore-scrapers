import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://store.tagheuer.com/us'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines(decode_unicode=True):
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if 'var allPosMarker' not in item:
                    lid = item.split(',')[0]
                    llat = item.split('"latitude":"')[1].split('"')[0]
                    llng = item.split('"longitude":"')[1].split('"')[0]
                    ltyp = item.split('"point_of_sale_type_name":')[1].split('}')[0].replace('"','')
                    if ltyp == 'null':
                        ltyp = '<MISSING>'
                    locs.append(lid + '|US|' + llat + '|' + llng + '|' + ltyp)
    url = 'https://store.tagheuer.com/ca'
    r = session.get(url, headers=headers)
    for line in r.iter_lines(decode_unicode=True):
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if 'var allPosMarker' not in item:
                    lid = item.split(',')[0]
                    llat = item.split('"latitude":"')[1].split('"')[0]
                    llng = item.split('"longitude":"')[1].split('"')[0]
                    ltyp = item.split('"point_of_sale_type_name":')[1].split('}')[0].replace('"','')
                    if ltyp == 'null':
                        ltyp = '<MISSING>'
                    locs.append(lid + '|CA|' + llat + '|' + llng + '|' + ltyp)
    for loc in locs:
        print(('Pulling Location %s...' % loc.split('|')[0]))
        website = 'tagheuer.com'
        country = loc.split('|')[1]
        lat = loc.split('|')[2]
        lng = loc.split('|')[3]
        typ = loc.split('|')[4]
        store = loc.split('|')[0]
        lurl = 'https://store.tagheuer.com/' + store
        r2 = session.get(lurl, headers=headers)
        lines = r2.iter_lines(decode_unicode=True)
        hours = '<MISSING>'
        phone = '<MISSING>'
        zc = '<MISSING>'
        city = '<MISSING>'
        add = '<MISSING>'
        for line2 in lines:
            if '<span class="components-outlet-item-name-basic__title__span">' in line2:
                name = next(lines).replace('\r','').replace('\t','').replace('\n','').strip()
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
            if '"addressLocality":"' in line2:
                city = line2.split('"addressLocality":"')[1].split('"')[0]
            if '"postalCode":"' in line2:
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '"telephone":"' in line2:
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if '"openingHours":"' in line2:
                hours = line2.split('"openingHours":"')[1].split('"')[0]
            if country == 'CA' and 'href="/ca/' in line2:
                next(lines)
                state = next(lines).split('"label":"')[1].split('"')[0]
            if country == 'US' and 'href="/us/' in line2:
                next(lines)
                state = next(lines).split('"label":"')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if zc == '0':
            zc = '<MISSING>'
        if ',' in city:
            state = city.split(',')[1].strip()
            city = city.split(',')[0].strip()
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
