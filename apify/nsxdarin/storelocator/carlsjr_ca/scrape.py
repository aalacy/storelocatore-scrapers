import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    url = 'https://www.carlsjr.ca/locations'
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    HFound = False
    for line in lines:
        if 'style="color:#FFC72C;">' in line or '<span style="color:#FFC72C">' in line:
            state = line.split('<span style="color:#')[1].split('>')[1].split('<')[0].strip()
        if '</span></span></span></p></div></div></div></div>' in line and '<footer' not in line:
            name = line.split('<span style="color:#2D2926">')[1].split('<')[0].strip()
            country = 'CA'
            typ = 'Restaurant'
            store = '<MISSING>'
            city = '<MISSING>'
            hours = ''
            zc = '<MISSING>'
            website = 'carlsjr.ca'
            lat = '<MISSING>'
            lng = '<MISSING>'
            addinfo = line.split('procn">')[2]
            if '<span style="color:#2D2926">' in addinfo:
                add = addinfo.split('<span style="color:#2D2926">')[1].split('<')[0]
            else:
                add = line.split('procn">')[2].split('<')[0].strip()
            next(lines)
            g = next(lines)
            if 'HOURS:' in g:
                HFound = True
                hours = g.split('HOURS:')[1].split('<')[0].strip().replace('&nbsp;',' ')
            else:
                if 'PH:' in g:
                    phone = g.split('PH:')[1].split('<')[0].strip()
                else:
                    phone = '<MISSING>'
        if '">HOURS:' in line:
            HFound = True
            hours = line.split('">HOURS:')[1].split('<')[0].strip().replace('&nbsp;',' ')
        if HFound and '<path d="M1.6' in line:
            HFound = False
            hours = hours.replace('&amp;','&').replace('&ndash;','-')
            add = add.replace('&nbsp;',' ').strip()
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if HFound and 'window.firstPageId' in line:
            HFound = False
            hours = hours.replace('&amp;','&').replace('&ndash;','-')
            add = add.replace('&nbsp;',' ').strip()
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if HFound and '">HOURS:' not in line and 'procn">' in line:
            hours = hours + '; ' + line.split('procn">')[1].split('<')[0]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
