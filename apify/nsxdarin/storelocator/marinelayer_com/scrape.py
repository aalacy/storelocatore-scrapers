import csv
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
    url = 'https://www.marinelayer.com/pages/stores'
    Found = True
    r = session.get(url, headers=headers)
    lines = r.iter_lines()
    website = 'marinelayer.com'
    typ = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    store = '<MISSING>'
    for line in lines:
        line = str(line.decode('utf-8'))
        if '<!-- END Southeast -->' in line:
            Found = False
        if Found and '</h5></li>' in line:
            name = line.split('<h5>')[1].split('<')[0]
            country = 'US'
            g = next(lines)
            g = str(g.decode('utf-8'))
            if '<a href="http://maps.google.com/?q' in g:
                addinfo = g.split('">')[1].split('</a>')[0]
                if addinfo.count('<br/>') == 2:
                    add = addinfo.split('<')[0] + ' ' + addinfo.split('<br/>')[1].strip()
                    city = addinfo.split('<br/>')[2].split(',')[0]
                    state = addinfo.split('<br/>')[2].split(',')[1].strip().split(' ')[0]
                    zc = addinfo.split('<br/>')[2].rsplit(' ',1)[1]
                else:
                    add = addinfo.split('<')[0]
                    city = addinfo.split('<br')[1].split('>')[1].split(',')[0]
                    state = addinfo.split('<br')[1].split('>')[1].split(',')[1].strip().split(' ')[0]
                    zc = addinfo.split('<br')[1].split('>')[1].rsplit(' ',1)[1]
            hours = ''
        if '<li>(' in line and Found:
            phone = line.split('<li>')[1].split('<')[0].strip()
        if '<li>Open' in line or '<li>TEMPORARILY CLOSED' in line or '<li>Mon-Sat' in line:
            if Found:
                loc = '<MISSING>'
                city = city.strip()
                state = state.strip()
                zc = zc.strip()
                if '<li>Open' in line:
                    hours = line.split('<li>Open')[1].split('<')[0].strip()
                elif '<li>TEMPORARILY CLOSED' in line:
                    hours = 'TEMPORARILY CLOSED'
                else:
                    hours = line.split('<li>')[1].strip().replace('\r','').replace('\n','')
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
