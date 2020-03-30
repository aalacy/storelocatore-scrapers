import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.tacobell.ca/en/stores/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'window.stores = [' in line:
            items = line.split('window.stores = [')[1].split('[')
            for item in items:
                if ']' in item:
                    sid = item.split('"]')[0].rsplit('"',1)[1]
                    lat = item.split(',')[0]
                    lng = item.split(',')[1]
                    lurl = 'https://www.tacobell.ca/en/store/' + sid
                    locs.append(lurl + '|' + lat + '|' + lng)
    
    for loc in locs:
        print('Pulling Location %s...' % loc.split('|')[0])
        website = 'tacobell.ca'
        typ = 'Restaurant'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'CA'
        store = '<MISSING>'
        phone = ''
        hours = ''
        lat = loc.split('|')[1]
        lng = loc.split('|')[2]
        r2 = session.get(loc.split('|')[0], headers=headers)
        for line2 in r2.iter_lines():
            if 'Taco Bell Canada | Locations | ' in line2:
                name = line2.split('Taco Bell Canada | Locations | ')[1].replace('\r','').replace('\n','').replace('\t','').strip()
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split('<')[0]
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split(',')[0]
                state = line2.split('itemprop="addressLocality">')[1].split(',')[1].strip().split(' ')[0]
                zc = line2.split('itemprop="addressLocality">')[1].split(',')[1].strip().split(' ',1)[1].split('<')[0]
            if 'itemprop="telephone">' in line2:
                phone = line2.split('itemprop="telephone">')[1].split('<')[0]
            if "itemprop='openingHours' datetime='" in line2:
                items = line2.split("itemprop='openingHours' datetime='")
                for item in items:
                    if "<span class='weekDay'>" in item:
                        if hours == '':
                            hours = item.split("<span class='weekDay'>")[1].split('<')[0] + ': ' + item.split("<span class='open'>")[1].split('<')[0] + '-' + item.split("<span class='close'>")[1].split('<')[0]
                        else:
                            hours = hours + '; ' + item.split("<span class='weekDay'>")[1].split('<')[0] + ': ' + item.split("<span class='open'>")[1].split('<')[0] + '-' + item.split("<span class='close'>")[1].split('<')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
