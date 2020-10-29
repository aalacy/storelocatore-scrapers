import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('dominos_ca')



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
    locs = []
    url = 'https://pizza.dominos.ca/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines(decode_unicode=True):
        if '<a rel="canonical" href="http://pizza.dominos.ca/' in line:
            items = line.split('class="location"><h2>')
            for item in items:
                if 'rel="canonical" href="' in item:
                    locs.append(item.split('rel="canonical" href="')[1].split('"')[0])
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        r2 = session.get(loc, headers=headers)
        website = 'dominos.ca'
        country = 'CA'
        typ = 'Store'
        store = loc.rsplit('-',1)[1].replace('/','')
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = ''
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<h1 itemprop="name">' in line2:
                name = line2.split('<h1 itemprop="name">')[1].split('<')[0]
            if 'id="Street" name="Street" value="' in line2:
                add = line2.split('id="Street" name="Street" value="')[1].split('"')[0]
            if 'id="City" name="City" value="' in line2:
                city = line2.split('id="City" name="City" value="')[1].split('"')[0]
            if 'id="Region" name="Region" value="' in line2:
                state = line2.split('id="Region" name="Region" value="')[1].split('"')[0]
            if 'id="PostalCode" name="PostalCode" value="' in line2:
                zc = line2.split('id="PostalCode" name="PostalCode" value="')[1].split('"')[0]
            if 'itemprop="telephone">' in line2:
                phone = line2.split('itemprop="telephone">')[1].split('<')[0]
            if 'itemprop="openingHours">' in line2:
                g = next(lines)
                hours = g.split('</table>')[0].strip().replace('\t','').replace('</td></tr><tr><td>','; ').replace('<tr><td>','').replace('</td></tr>','').replace('</td><td>',': ')
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
