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
    url = 'http://mjmdesignershoes.com/shipad_mjmshoes.html'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    website = 'mjmdesignershoes.com'
    typ = '<MISSING>'
    country = 'US'
    loc = '<MISSING>'
    hours = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if '<td class="findastore" valign="top">' in line:
            store = line.split('<b>')[1].split(')')[0]
            name = line.split('</b>')[1].split('<')[0].strip()
            add = next(lines).split('<')[0].strip().replace('\t','')
            g = next(lines)
            if '<a href' not in g:
                add = add + ' ' + g.split('<')[0].strip().replace('\t','')
                g = next(lines)
            csz = g.split('">')[1].split('<')[0]
            zc = csz.rsplit(' ',1)[1]
            city = csz.split(',')[0]
            state = csz.split(',')[1].strip().split(' ')[0]
            g = next(lines)
            phone = g.split('<')[0].strip().replace('\t','')
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
