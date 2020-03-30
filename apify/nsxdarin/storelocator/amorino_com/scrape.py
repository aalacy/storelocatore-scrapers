import csv
import urllib2
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
    USFound = False
    for line in r.iter_lines():
        if '<optgroup label="USA">' in line:
            USFound = True
        if USFound and '<option value="https://www.amorino.com/us/' in line:
            if '/city/' in line:
                cities.append(line.split('value="')[1].split('"')[0])
            else:
                locs.append(line.split('value="')[1].split('"')[0])

    for city in cities:
        print('Pulling City %s...' % city)
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            if ' class="bouton">' in line2:
                locs.append(line2.split('href="')[1].split('"')[0])

    for loc in locs:
        print('Pulling Location %s...' % loc)
        r2 = session.get(loc, headers=headers)
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
        for line2 in r2.iter_lines():
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
                    address = address.encode('utf-8')
                    if address == '':
                        address = '<INACCESSIBLE>'
                    city = add[0]['PlaceName'].encode('utf-8')
                    state = add[0]['StateName'].encode('utf-8')
                    zc = add[0]['ZipCode'].encode('utf-8')
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
