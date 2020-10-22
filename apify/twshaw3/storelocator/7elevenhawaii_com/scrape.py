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
    url = 'https://7elevenhawaii.com/locations/'
    r = session.get(url, headers=headers)
    website = '7elevenhawaii.com'
    country = 'US'
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<h2 class="tg-item-title"><a href="https://7elevenhawaii.com/' in line:
            items = line.split('<h2 class="tg-item-title"><a href="https://7elevenhawaii.com/')
            for item in items:
                if 'data-sortbyload =""' not in item:
                    lurl = 'https://7elevenhawaii.com/' + item.split('"')[0]
                    locs.append(lurl)
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = 'HI'
        zc = ''
        store = '<MISSING>'
        phone = ''
        typ = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = 'Sun-Sat: 24 Hours'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode('utf-8'))
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' - ')[0].encode("ascii", errors="ignore").decode()
            if '<p class="sow-more-text">' in line2 and add == '':
                g = next(lines)
                g = str(g.decode('utf-8')).replace('\r','').replace('\t','').replace('\n','').strip()
                add = g.split(' — ')[0].encode("ascii", errors="ignore").decode()
                city = g.split(' — ')[1].split(',')[0].encode("ascii", errors="ignore").decode()
                zc = g.rsplit(' ',1)[1]
                if '<' in zc:
                    zc = zc.split('<')[0]
            if 'Contact Us' in line2:
                next(lines)
                g = next(lines)
                g = str(g.decode('utf-8')).replace('\r','').replace('\t','').replace('\n','').strip()
                phone = g
            if 'google.com' in line2 and '/@' in line2:
                lat = line2.split('/@')[1].split(',')[0]
                lng = line2.split('/@')[1].split(',')[1]
        phone = phone.replace('<p>','').replace('</p>','')
        name = name.replace('&#039;',"'")
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
