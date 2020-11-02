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
    url = 'https://gorjana.com/pages/store-locator'
    r = session.get(url, headers=headers)
    website = 'gorjana.com'
    country = 'US'
    typ = '<MISSING>'
    loc = '<MISSING>'
    store = '<MISSING>'
    lat = '<MISSING>'
    lng = '<MISSING>'
    lines = r.iter_lines()
    Found = False
    for line in lines:
        line = str(line.decode('utf-8'))
        if Found is False and 'var storeMarkers' in line:
            Found = True
        if Found and '</script>' in line:
            Found = False
        if Found and 'id: ' in line:
            store = line.split('id: ')[1].split(',')[0]
            g = next(lines)
            g = str(g.decode('utf-8'))
            name = g.split('title: `')[1].split('`')[0]
            g = next(lines)
            g = str(g.decode('utf-8'))
            g = g.split(': `')[1].split('`')[0]
            if g.count('<br />') == 0:
                add = g.split(',')[0].strip() + ' ' + g.split(',')[1].strip()
                city = g.split(',')[2].strip()
                state = g.split(',')[3].strip().split(' ')[0]
                zc = g.rsplit(' ',1)[1]
            elif g.count('<br />') == 1:
                add = g.split('<br')[0]
                city = g.split('<br />')[1].split(',')[0]
                state = g.split('<br />')[1].split(',')[1].strip().split(' ')[0]
                zc = g.rsplit(' ',1)[1]
            else:
                add = g.split('<br />')[0].strip() + ' ' + g.split('<br />')[1].strip()
                city = g.split('<br />')[2].split(',')[0]
                state = g.split('<br />')[2].split(',')[1].strip().split(' ')[0]
                zc = g.rsplit(' ',1)[1]
        if Found and 'phone: `' in line:
            phone = line.split('phone: `')[1].split('`')[0]
        if Found and 'working_hours: `' in line:
            hours = line.split('working_hours: `')[1].split('`')[0].replace('<br />','; ').replace('|',':')
            if hours == '':
                hours = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
