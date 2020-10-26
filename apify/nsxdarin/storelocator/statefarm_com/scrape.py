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
    states = []
    cities = []
    url = 'https://www.statefarm.com/agent/us'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'class="block"   >' in line:
            states.append('https://www.statefarm.com' + line.split('href="')[1].split('"')[0])
    for state in states:
        r2 = session.get(state, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        print(('Pulling State %s...' % state))
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'class="block"   >' in line2:
                cities.append('https://www.statefarm.com' + line2.split('href="')[1].split('"')[0])
    for city in cities:
        r2 = session.get(city, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        #print('Pulling City %s...' % city)
        country = 'US'
        typ = '<MISSING>'
        website = 'statefarm.com'
        hours = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        loc = '<MISSING>'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if "getEmailPageAL('" in line2:
                store = line2.split("getEmailPageAL('")[1].split("'")[0]
            if '<span class="sfx-text agentListAgentName"><h4>' in line2:
                phone = ''
                store = ''
                loc = ''
                hours = ''
                name = line2.split('<span class="sfx-text agentListAgentName"><h4>')[1].replace('\r','').replace('\t','').replace('\n','').strip()
            if '<a href="https://www.statefarm.com/agent/' in line2:
                g = next(lines)
                if g.count('<br/>') == 1:
                    add = g.split('<br/>')[0].strip().replace('\t','')
                    csz = g.split('<br/>')[1].replace('\t','').replace('\r','').replace('\n','').strip()
                    city = csz.split(',')[0]
                    state = csz.split('&nbsp;')[1]
                    zc = csz.split('&nbsp;')[2]
                else:
                    add = g.split('<br/>')[0].strip().replace('\t','')
                    add = add + ' ' + g.split('<br/>')[1].strip().replace('\t','')
                    csz = g.split('<br/>')[2].replace('\t','').replace('\r','').replace('\n','').strip()
                    city = csz.split(',')[0]
                    state = csz.split('&nbsp;')[1]
                    zc = csz.split('&nbsp;')[2]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if '<span id="officeHour' in line2:
                if hours == '':
                    hours = line2.split('<span id="officeHour')[1].split('>')[1].split('<')[0].strip()
                else:
                    hours = hours + '; ' + line2.split('<span id="officeHour')[1].split('>')[1].split('<')[0].strip()
            if 'id="visitAgentSite' in line2:
                loc = line2.split('href="')[1].split('"')[0]
                if phone == '':
                    phone = '<MISSING>'
                if hours == '':
                    hours = '<MISSING>'
                if loc not in locs:
                    locs.append(loc)
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
