import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import sgzip
import time
import usaddress

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = []
    for code in sgzip.for_radius(100):
        print(('Pulling Zip Code %s...' % code))
        url = 'https://bobcat.know-where.com/bobcat/cgi/selection?place=' + code + '&lang=en&option=&ll=&stype=place&async=results'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        time.sleep(3)
        lines = r.iter_lines(decode_unicode=True)
        for line in lines:
            website = 'bobcat.com'
            if 'kw-results-FIELD-NAME' in line:
                name = line.split('kw-results-FIELD-NAME">')[1].split('<')[0]
                typ = 'Dealer'
                print(name)
            if '<span onclick="KW.bobcat.toggleDetail' in line:
                store = line.split("toggleDetail('")[1].split("'")[0]
                raw_address = next(lines).split('<div>')[1].split('</div>')[0]
                tel_line = next(lines)
                while 'tel:' not in tel_line:
                    tel_line = next(lines)
                phone = tel_line.split('tel:')[1].split('"')[0]
                print(phone)
                try:
                    tagged = usaddress.tag(raw_address)[0]
                    city = tagged.get('PlaceName', '<MISSING>')
                    state = tagged.get('StateName', '<MISSING>')
                    zc = tagged.get('ZipCode', '<MISSING>')
                    if city != '<MISSING>':
                        add = raw_address.split(city)[0].strip() 
                    else:
                        add = raw_address.split(',')[0]
                except:
                    zc = add.strip().rsplit(' ')[1]
                    state = add.strip().split(' ')[-2]
                    city = add.strip().split(',')[0].split(' ')[1]
                    add = add.strip().split(',')[0].split(' ')[0]
                print(add)
                print(city)
                print(state)
                print(zc)
                country = 'US'
                hours = '<MISSING>'
            if 'poilat: "' in line:
                lat = line.split('poilat: "')[1].split('"')[0].replace('+','')
            if 'poilon: "' in line:
                lng = line.split('poilon: "')[1].split('"')[0].replace('-0','-')
                if store not in ids:
                    ids.append(store)
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
