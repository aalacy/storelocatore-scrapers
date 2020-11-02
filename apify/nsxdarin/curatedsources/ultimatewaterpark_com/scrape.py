import csv
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('ultimatewaterpark_com')



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
    url = 'https://www.ultimatewaterpark.com/waterparks/parks_by_name.php'
    r = session.get(url, headers=headers)
    website = 'ultimatewaterpark.com'
    Found = True
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<p class="secnav">' in line:
            Found = False
        if Found and '<li><a href="' in line:
            if ' &ndash; ' not in line:
                lurl = 'https://www.ultimatewaterpark.com/waterparks/' + line.split('"')[1].split('"')[0]
                locs.append(lurl)
    for loc in locs:
        logger.info('Pulling Location %s...' % loc)
        country = 'US'
        state = ''
        zc = ''
        add = ''
        city = ''
        name = ''
        phone = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode('utf-8'))
            if '<title>' in line2:
                name = line2.split('<title>')[1].split('<')[0]
                if '|' in name:
                    name = name.split('|')[0].strip()
            if '<div class="wpLocation">' in line2:
                g = next(lines)
                h = next(lines)
                g = str(g.decode('utf-8'))
                h = str(h.decode('utf-8'))
                csz = h.strip().replace('\t','').replace('\r','').replace('\n','')
                add = g.split('<')[0].strip().replace('\t','')
                if '&ndash; Canada' not in csz:
                    zc = csz.rsplit(' ',1)[1]
                    city = csz.split(',')[0]
                    state = csz.split(',')[1].strip().split(' ')[0]
                else:
                    country = 'CA'
                    city = csz.split(',')[0]
                    state = csz.split(',')[1].strip().split(' ')[0]
                    zc = csz.split(',')[1].strip().split(' ',1)[1].strip()
            if '<p>(' in line2:
                phone = line2.split('<p>')[1].split('<')[0]
                if ' (' in phone:
                    phone = phone.split(' (')[0]
        typ = '<MISSING>'
        store = '<MISSING>'
        hours = '<MISSING>'
        if zc == '':
            zc = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        name = name.replace('&eacute;','e').replace('&egrave;','e').replace('&amp;','&')
        add = add.replace('&eacute;','e').replace('&egrave;','e').replace('&amp;','&')
        city = city.replace('&eacute;','e').replace('&egrave;','e').replace('&amp;','&')
        state = state.replace('&eacute;','e').replace('&egrave;','e').replace('&amp;','&')
        if '&ndash;' in zc:
            zc = zc.split('&ndash;')[0].strip()
        if country == 'CA' or country == 'US':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
