import csv
import urllib.request, urllib.error, urllib.parse
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
    url = 'http://borregodeoro.com/contact.html'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    typ = 'Restaurant'
    website = 'borregodeoro.com'
    country = 'US'
    lat = '<MISSING>'
    lng = '<MISSING>'
    hours = '<MISSING>'
    Found = True
    num = 0
    lines = r.iter_lines(decode_unicode=True)
    maps = []
    locs = []
    for line in lines:
        if '<iframe src="https://www.google.com/maps/' in line:
            maplat = line.split('!2d')[1].split('!')[0]
            maplng = line.split('!3d')[1].split('!')[0]
            maps.append(maplat + ',' + maplng)
        if 'Contact</p></div></a>' in line:
            Found = True
        if Found and '<div class="colelem"' in line:
            Found = False
        if Found and 'div class="clearfix grpelem"' in line:
            num = num + 1
            name = 'Borrego ' + str(num)
            store = str(num)
            add = next(lines).split('>')[1].split('<')[0]
            g = next(lines)
            city = g.split('>')[1].split(',')[0]
            state = g.split('>')[1].split(',')[1].strip().split(' ')[0]
            zc = g.split(',')[1].split('<')[0].rsplit(' ',1)[1]
            next(lines)
            phone = next(lines).split('>')[1].split('<')[0].replace('&#45;','-')
            locs.append(name + '|' + add + '|' + city + '|' + state + '|' + zc + '|' + phone + '|' + store)
    for x in range(0, len(locs)):
        name = locs[x].split('|')[0]
        add = locs[x].split('|')[1]
        city = locs[x].split('|')[2]
        state = locs[x].split('|')[3]
        zc = locs[x].split('|')[4]
        phone = locs[x].split('|')[5]
        lat = maps[x].split(',')[0]
        lng = maps[x].split(',')[1]
        store = locs[x].split('|')[6]
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
