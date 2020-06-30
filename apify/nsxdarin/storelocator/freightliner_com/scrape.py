import csv
import urllib2
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
    urls = ['https://freightliner.com/dealers/CANADA','https://freightliner.com/dealers/UNITED-STATES']
    for url in urls:
        r = session.get(url, headers=headers)
        website = 'freightliner.com'
        if 'CANADA' in url:
            country = 'CA'
        else:
            country = 'US'
        for line in r.iter_lines():
            if '<h2><a href="/Dealer?code=' in line:
                code = line.split('<h2><a href="/Dealer?code=')[1].split('&')[0]
                lurl = 'https://freightliner.com/Dealer?code=' + code
                print(lurl)
                r2 = session.get(lurl, headers=headers)
                name = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                store = code
                typ = '<MISSING>'
                lat = '<MISSING>'
                lng = '<MISSING>'
                hours = ''
                phone = ''
                HFound = False
                lines = r2.iter_lines()
                for line2 in lines:
                    if '<h3><a map="' in line2:
                        if country == 'CA':
                            zc = line2.split('<h3><a map="')[1].split('"')[0].strip().replace('\t','')[-7:]
                        else:
                            zc = line2.split('<h3><a map="')[1].split('"')[0].strip().replace('\t','').rsplit(' ',1)[1]
                    if '"name": "' in line2:
                        name = line2.split('"name": "')[1].split('"')[0].replace('&amp;','')
                    if '"addressLocality": "' in line2:
                        city = line2.split('"addressLocality": "')[1].split('"')[0]
                    if '"addressRegion": "' in line2:
                        state = line2.split('"addressRegion": "')[1].split('"')[0]
                    if '"streetAddress": "' in line2:
                        add = line2.split('"streetAddress": "')[1].split('"')[0]
                    if '"telephone": "' in line2:
                        phone = line2.split('"telephone": "')[1].split('"')[0]
                    if '<h4>Sales</h4>' in line2:
                        HFound = True
                    if HFound and '</item-department>' in line2:
                        HFound = False
                    if HFound and 'day:</header>' in line2:
                        day = line2.split('>')[1].split('<')[0]
                        g = next(lines)
                        if '>' not in g:
                            g = next(lines)
                        day = day + ' ' + g.split('>')[1].split('<')[0]
                        if hours == '':
                            hours = day
                        else:
                            hours = hours + '; ' + day
                if hours == '':
                    hours = '<MISSING>'
                yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
