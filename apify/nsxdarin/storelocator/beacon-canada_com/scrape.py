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
    url = 'https://beacon-canada.com/Contact_Us.html'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    name = ''
    hours = ''
    for line in lines:
        if '<td width="33%"' in line and '><span style="font-weight: bold">' in line:
            if 'Posi-' in line:
                hours = '<MISSING>'
            name = line.split('><span style="font-weight: bold">')[1].split('<')[0]
            if '<strong>(' in line:
                name = name + ' ' + line.split('<strong>')[1].split('<')[0]
            if '<strong> (' in line:
                name = name + line.split('<strong>')[1].split('<')[0]
            g = next(lines)
            add = ''
            if '<span itemprop="streetAddress">' in g:
                add = '#1 - 7688 - 132 Street'
                city = 'Surrey'
                zc = 'V3W 4M9'
            if '311 Chemin' in g:
                g = '311 Chemin Saint Francois Xavier'
            else:
                g = g.split('<')[0].strip().replace('\t','')
            h = next(lines)
            if 'al, QC' in h:
                h = 'Montreal, QC H1A 1A9'
            else:
                h = h.split('<')[0].strip().replace('\t','')
            if '132 Street' not in add:
                add = g
            loc = '<MISSING>'
            website = 'beacon-canada.com'
            if '132 Street' not in add:
                city = h.split(',')[0]
                zc = h.strip().rsplit(' ',2)[1] + ' ' + h.rsplit(' ',1)[1]
            country = 'CA'
            lat = '<MISSING>'
            lng = '<MISSING>'
            store = '<MISSING>'
            typ = '<MISSING>'
        if 'Posi-Pentes</span><br />' in line:
            add = '13145 Rue Prince Arthur'
            city = 'Montreal'
            state = 'Quebec'
            zc = 'H1A 1A9'
            name = 'Posi-Pentes'
            phone = '(514) 642-8691'
        if 'https://www.google.com/maps/place/' in line and '@' in line:
            lat = line.split('@')[1].split(',')[0]
            lng = line.split('@')[1].split(',')[1]
        if '<td scope="col"><span style="font-weight: bold">' in line and 'Posi-Slope' not in line and '><span style="font-weight: bold">' in line:
            name = line.split('><span style="font-weight: bold">')[1].split('<')[0]
            if '<strong>(' in line:
                name = name + ' ' + line.split('<strong>')[1].split('<')[0]
            if '<strong> (' in line:
                name = name + line.split('<strong>')[1].split('<')[0]
            g = next(lines).split('<')[0].strip().replace('\t','')
            h = next(lines)
            if 'Trois-R' in h:
                h = 'Trois-Rivieres, QC G9C 1M6'
            elif 'bec, QC G1P 3X2' in h:
                h = 'Quebec, QC G1P 3X2'
            else:
                h = h.split('<')[0].strip().replace('\t','')
            add = g
            loc = '<MISSING>'
            website = 'beacon-canada.com'
            city = h.split(',')[0]
            zc = h.strip().rsplit(' ',2)[1] + ' ' + h.rsplit(' ',1)[1]
            country = 'CA'
            lat = '<MISSING>'
            lng = '<MISSING>'
            store = '<MISSING>'
            typ = '<MISSING>'
        if 'Locations </span>' in line:
            if 'bec Locations' in line:
                state = 'Quebec'
            else:
                state = line.split('<h2><span style="font-weight: bold">')[1].split(' Locations')[0]
        if 'PH: (' in line:
            phone = line.split('PH: ')[1].split('<')[0]
        if '">Open:' in line:
            hours = line.split('">Open:')[1].split('</span>')[0].strip().replace('&#8226;','; ').replace('  ',' ')
        if 'Get Driving Directions' in line:
            if hours != '<MISSING>':
                hours = hours.replace('<span class="style3" style="font-weight: bold; font-size: 11px">','')
                hours = hours.replace(' ;',';')
            if name != '':
                if 'Mississauga' in city or 'Peterborough' in city:
                    state = 'Ontario'
                if 'Surrey' in city:
                    state = 'British Columbia'
                if 'al, QC' in name:
                    name = 'Montreal, QC'
                if 'bec, QC' in name:
                    name = 'Quebec, QC'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
