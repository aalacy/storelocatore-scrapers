import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('goodwill_org')



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
    for x in range(0, 6000):
        logger.info((str(x)))
        url = 'https://www.goodwill.org/location/?store=' + str(x)
        Found = False
        website = 'goodwill.org'
        typ = '<MISSING>'
        hours = ''
        name = ''
        state = ''
        add = ''
        city = ''
        country = 'US'
        phone = ''
        zc = ''
        lat = ''
        lng = ''
        store = str(x)
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        lines = r.iter_lines(decode_unicode=True)
        loc = url
        for line in lines:
            if "<hr><div class='" in line:
                tp = line.split("<hr><div class='")[1].split('>')[1].split('<')[0]
                if typ == '<MISSING>':
                    typ = tp
                else:
                    typ = typ + '; ' + tp
            if '<h4>Details</h4>' in line:
                g = next(lines)
                h = next(lines)
                i = next(lines)
                if '<span></span>' not in g:
                    name = g.split('<span>')[1].split('<')[0]
                    add = g.split('<br />')[1]
                    if '<br />' in h:
                        g = g.replace('\r','').replace('\n','') + h
                    if '<br />' in i:
                        g = h.replace('\r','').replace('\n','') + i
                    if 'United States' in g.split('<br />')[3]:
                        csz = g.split('<br />')[2]
                        phone = g.split('<br />')[4]
                    elif 'United States' in g.split('<br />')[4]:
                        add = add + ' ' + g.split('<br />')[2]
                        csz = g.split('<br />')[3]
                        phone = g.split('<br />')[5]
                    elif 'United States' in g.split('<br />')[5]:
                        add = add + ' ' + g.split('<br />')[2] + ' ' + g.split('<br />')[3]
                        csz = g.split('<br />')[4]
                        phone = g.split('<br />')[6]
                    csz = csz.replace(',,',',')
                    city = csz.split(',')[0]
                    state = csz.split(',')[1].strip().split(' ')[0]
                    zc = csz.split(',')[1].rsplit(' ',1)[1]
            if '//addMarker(' in line and 'lat' not in line:
                lat = line.split('//addMarker(')[1].split(',')[0]
                lng = line.split('//addMarker(')[1].split(',')[1].strip().split(')')[0]
            if '<div class="hours">' in line:
                Found = True
            if Found and '</div>' in line and '<hr>' not in line:
                Found = False
            if Found and 'DAY -' in line:
                hrs = line.split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if name != '':
            if '; MONDAY' in hours:
                hours = hours.split('; MONDAY')[0]
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
