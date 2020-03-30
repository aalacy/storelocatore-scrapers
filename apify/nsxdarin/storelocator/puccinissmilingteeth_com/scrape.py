import csv
import urllib2
from sgrequests import SgRequests

requests.packages.urllib3.disable_warnings()

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
    url = 'https://www.puccinissmilingteeth.com/locations-2/'
    locs = []
    Found = False
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        if 'Our Locations</h3>' in line:
            Found = True
        if Found and '</div>' in line:
            Found = False
        if Found and '<a href="https://www.puccinissmilingteeth.com/' in line:
            locs.append(line.split('href="')[1].split('"')[0] + '|' + cs)
        if '<p><strong>' in line:
            cs = line.split('<p><strong>')[1].split('<')[0]
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        HFound = False
        lurl = loc.split('|')[0]
        city = loc.split('|')[1].split(',')[0]
        state = loc.split('|')[1].split(',')[1].strip()
        name = ''
        add = ''
        store = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = ''
        country = 'US'
        zc = '<MISSING>'
        phone = ''
        print('Pulling Location %s...' % loc)
        website = 'puccinissmilingteeth.com'
        typ = 'Restaurant'
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            if '<title>' in line2:
                name = line2.split('<title>')[1].split('<')[0].replace('&#8211;','-').replace('&#039;',"'").rsplit(' - ',1)[0]
            if '<p><strong>' in line2:
                add = line2.split('<p><strong>')[1].split('<')[0].strip().replace('\t','')
                try:
                    phone = line2.split('tel:')[1].split('"')[0]
                except:
                    phone = line2.split('<strong>')[2].split('<')[0]
            if 'Hours:</big></h5>' in line2:
                HFound = True
            if HFound and '<br />' in line2:
                hrs = line2.split('<br')[0].replace('<p>','').replace('<small>','')
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if HFound and '</small>' in line2:
                HFound = False
        hours = hours.replace('&#8211;','-')
        yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
