import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import sgzip
import time

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
        Found = False
        time.sleep(3)
        lines = r.iter_lines(decode_unicode=True)
        for line in lines:
            if '"><span class="kw-results-FIELD-NAME">' in line:
                name = line.split('"><span class="kw-results-FIELD-NAME">')[1].split('<')[0]
                website = 'bobcat.com'
                typ = 'Dealer'
            if Found is False and '<span onclick="KW.bobcat.toggleDetail' in line:
                store = line.split("toggleDetail('")[1].split("'")[0]
                Found = True
                g = next(lines)
                h = next(lines)
                next(lines)
                i = next(lines)
                phone = i.split('">')[1].split('<')[0]
                add = g.split('>')[1].split('<')[0]
                city = h.split('>')[1].split(',')[0]
                state = h.split('>')[1].split(',')[1].strip().split(' ')[0]
                zc = h.split('>')[1].split('<')[0].rsplit(' ',1)[1]
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
