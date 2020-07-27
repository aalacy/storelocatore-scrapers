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
    alllocs = []
    page = 0
    Found = True
    while Found:
        locs = []
        Found = False
        page = page + 1
        print('Page: ' + str(page))
        url = 'https://www.policeone.com/law-enforcement-directory/search/page-' + str(page)
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            line = str(line.decode('utf-8'))
            if '<a class="Table-row " data-js-hover href="' in line:
                Found = True
                lurl = 'https://www.policeone.com' + line.split('href="')[1].split('"')[0]
                if lurl not in alllocs:
                    locs.append(lurl)
                    alllocs.append(lurl)
        for loc in locs:
            r = session.get(loc, headers=headers)
            #print(loc)
            country = 'US'
            website = 'policeone.com/law-enforcement-directory'
            name = ''
            add = ''
            city = ''
            state = ''
            zc = ''
            store = '<MISSING>'
            phone = ''
            lat = '<MISSING>'
            lng = '<MISSING>'
            hours = '<MISSING>'
            lines = r.iter_lines()
            for line in lines:
                line = str(line.decode('utf-8'))
                if '<title>' in line:
                    name = line.split('<title>')[1].split('<')[0]
                if 'Country:</dt>' in line:
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    country = g.split('>')[1].split('<')[0]
                    if 'States' in country:
                        country = 'US'
                    if 'Canada' in country:
                        country = 'CA'
                if 'Address 1:</dt>' in line:
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    add = g.split('>')[1].split('<')[0]
                if 'Address 2:</dt>' in line:
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    add = add + ' ' + g.split('>')[1].split('<')[0]
                if 'City:</dt>' in line:
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    city = g.split('>')[1].split('<')[0]
                if 'State:</dt>' in line:
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    state = g.split('>')[1].split('<')[0]
                if 'Zip Code:</dt>' in line:
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    zc = g.split('>')[1].split('<')[0]
                if 'Phone #:</dt>' in line:
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    phone = g.split('>')[1].split('<')[0]
                if 'Type:</dt>' in line:
                    g = next(lines)
                    g = str(g.decode('utf-8'))
                    typ = g.split('>')[1].split('<')[0]
            if country == 'US' or country == 'CA':
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
