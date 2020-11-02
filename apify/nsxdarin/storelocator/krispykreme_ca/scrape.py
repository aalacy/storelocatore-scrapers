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
    url = 'https://krispykreme.ca/find-a-store/'
    r = session.get(url, headers=headers)
    website = 'krispykreme.ca'
    typ = '<MISSING>'
    country = 'CA'
    lines = r.iter_lines()
    loc = '<MISSING>'
    names = []
    store = '<MISSING>'
    for line in lines:
        line = str(line.decode('utf-8'))
        if '!2d' in line:
            lng = line.split('!2d')[1].split('!')[0]
            lat = line.split('!3d')[1].split('!')[0]
        if '<div class="location__title h2 text-uppercase">' in line:
            g = next(lines)
            g = str(g.decode('utf-8'))
            name = g.strip().replace('\r','').replace('\t','').replace('\n','')
        if '<div class="location__address">' in line:
            g = next(lines)
            h = next(lines)
            i = next(lines)
            j = next(lines)
            g = str(g.decode('utf-8'))
            h = str(h.decode('utf-8'))
            i = str(i.decode('utf-8'))
            j = str(j.decode('utf-8'))
            if '</div>' in j:
                add = g.split('<')[0]
                city = h.split('<')[0].rsplit(' ',1)[0].replace(',','').strip().replace('\r','').replace('\t','').replace('\n','')
                state = h.split('<')[0].rsplit(' ',1)[1]
                zc = i.strip().replace('\r','').replace('\t','').replace('\n','').replace('<br />','')
            else:
                add = g.split('<')[0] + ' ' + h.split('<')[0]
                city = i.split('<')[0].rsplit(' ',1)[0].replace(',','').strip().replace('\r','').replace('\t','').replace('\n','')
                state = i.split('<')[0].rsplit(' ',1)[1]
                zc = j.strip().replace('\r','').replace('\t','').replace('\n','').replace('<br />','')
        if '<strong>Tel:</strong>' in line:
            phone = line.split('<strong>Tel:</strong>')[1].replace(',','').strip().replace('\r','').replace('\t','').replace('\n','')
        if '<div class="location__hours">' in line:
            g = next(lines)
            h = next(lines)
            g = str(g.decode('utf-8'))
            h = str(h.decode('utf-8'))
            if 'Delivery Via' not in g:
                hours = g.split('">')[1].split('<')[0] + ': ' + h.split('<div>')[1].split('<')[0]
            if add not in names:
                names.append(add)
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
