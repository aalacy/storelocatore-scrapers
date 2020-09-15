import csv
from sgrequests import SgRequests
import re

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
    r = session.get('https://www.bubbagump.com/locations.asp?view=all', headers=headers)
    lines = r.iter_lines()
    website = 'bubbagump.com'
    typ = 'Restaurant'
    hours = ''
    HFound = False
    for line in lines:
        line = str(line.decode('utf-8'))
        if 'style="border-style:none;" align="center"' in line:
            store = line.split('/img/locations/')[1].split('.')[0]
        if '<!--========= End Locations Hours =========-->' in line:
            if country == 'US' or country == 'CA':
                if hours == '':
                    hours = '<MISSING>'
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if '<div class="search_location_name desktop">' in line:
            name = line.split('class="white_chunk_text">')[1].split('<')[0].strip()
            purl = 'https://www.bubbagump.com' + line.split('href="')[1].split('"')[0]
        if 'name="geo.region" content="' in line:
            hours = ''
            country = line.split('name="geo.region" content="')[1].split('-')[0]
            state = line.split('name="geo.region" content="')[1].split('-')[1].split('"')[0]
        if 'Dining Rooms:</strong><br />' in line:
            HFound = True
        if HFound and '<li style="' in line and 'Dining Rooms' not in line:
            HFound = False
        if HFound and 'Dining Rooms:</strong><br />' not in line:
            if 'day' in line or '&nbsp;' in line or 'Daily' in line or 'Sun' in line:
                if hours == '':
                    hours = line.replace('\t','').replace('\r','').replace('\n','').strip().replace('&nbsp;',' ').replace('<br />','; ').replace('<div class=""float_left desktop"">','').replace('</div>','').strip().replace('Daily','Daily:')
                else:
                    hours = hours + '; ' + line.replace('\t','').replace('\r','').replace('\n','').strip().replace('&nbsp;',' ').replace('<br />','; ').replace('<div class=""float_left desktop"">','').replace('</div>','').strip().replace('Daily','Daily:')
            cleanr = re.compile('<.*?>')
            hours = re.sub(cleanr, '', hours)
            hours = hours.replace(':;',':')
            hours = hours.replace('day;','day:')
        if '<meta name="ICBM" content="' in line:
            lat = line.split('<meta name="ICBM" content="')[1].split(',')[0]
            lng = line.split('<meta name="ICBM" content="')[1].split(',')[1].split('"')[0].strip()
            g = next(lines)
            g = str(g.decode('utf-8'))
            if '<strong>' not in g:
                g = next(lines)
                g = str(g.decode('utf-8'))
            if country == 'US' or country == 'CA':
                phone = g.split('<span class="desktop">Ph:')[1].split('<')[0].strip()
                add = g.split('<strong>')[1].split('<')[0]
                city = g.split('<br class="mobile" /><br/>')[1].split(',')[0]
                zc = g.split('<br class="mobile" /><br/>')[1].split('<')[0].strip().split('  ')[1].strip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
