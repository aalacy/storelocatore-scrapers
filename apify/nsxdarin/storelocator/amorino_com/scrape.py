import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
import usaddress

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "raw_address", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.amorino.com/us/shops.html'
    locs = []
    cities = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    USFound = False
    for line in r.iter_lines(decode_unicode=True):
        if '<optgroup label="USA">' in line:
            USFound = True
        if USFound and '<option value="https://www.amorino.com/us/' in line:
            if '/city/' in line:
                cities.append(line.split('value="')[1].split('"')[0])
            else:
                locs.append(line.split('value="')[1].split('"')[0])

    for city in cities:
        print(('Pulling City %s...' % city))
        r2 = session.get(city, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if ' class="bouton">' in line2:
                locs.append(line2.split('href="')[1].split('"')[0])

    for loc in locs:
        print(('Pulling Location %s...' % loc))
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        website = 'amorino.com'
        country = 'US'
        store = loc.replace('.html','').rsplit('.',1)[1]
        typ = 'Boutique'
        hours = '<MISSING>'
        name = ''
        address = ''
        city = ''
        state = ''
        zc = ''
        phone = '<MISSING>'
        lat = ''
        lng = ''
        rawadd = ''
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<title>' in line2:
                name = line2.split('<title>')[1].split('<')[0].replace('Amorino - ','')
            if '<li><i class="fa fa-map-marker"></i>' in line2:
                rawadd = line2.split('<li><i class="fa fa-map-marker"></i>')[1].split('<')[0].strip()
                try:
                    add = usaddress.tag(rawadd)
                    baseadd = add[0]
                    if 'AddressNumber' not in baseadd:
                        baseadd['AddressNumber'] = ''
                    if 'StreetName' not in baseadd:
                        baseadd['StreetName'] = ''
                    if 'StreetNamePostType' not in baseadd:
                        baseadd['StreetNamePostType'] = ''
                    if 'PlaceName' not in baseadd:
                        baseadd['PlaceName'] = '<INACCESSIBLE>'
                    if 'StateName' not in baseadd:
                        baseadd['StateName'] = '<INACCESSIBLE>'
                    if 'ZipCode' not in baseadd:
                        baseadd['ZipCode'] = '<INACCESSIBLE>'
                    address = add[0]['AddressNumber'] + ' ' + add[0]['StreetName'] + ' ' + add[0]['StreetNamePostType']
                    address = address
                    if address == '':
                        address = '<INACCESSIBLE>'
                    city = add[0]['PlaceName']
                    state = add[0]['StateName']
                    zc = add[0]['ZipCode']
                except:
                    pass
            if 'Tel : ' in line2:
                phone = line2.split('Tel : ')[1].split('<')[0].strip().replace(' ','-')
            if 'new google.maps.LatLng(' in line2:
                lat = line2.split('new google.maps.LatLng(')[1].split(',')[0]
                lng = line2.split(',')[1].split(')')[0]
            if "<i class='fa fa-clock-o'></i>" in line2:
                hours = line2.split("<i class='fa fa-clock-o'></i>")[1].split('</ul>')[0].replace('\t','').strip().replace('<br/>','; ').replace('&nbsp;','')
        if address == '':
            address = '<INACCESSIBLE>'
        if city == '':
            city = '<INACCESSIBLE>'
        if state == '':
            state = '<INACCESSIBLE>'
        if zc == '':
            zc = '<INACCESSIBLE>'
        yield [website, name, rawadd, address, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
