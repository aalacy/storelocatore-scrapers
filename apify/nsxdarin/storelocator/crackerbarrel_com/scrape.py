import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import gzip

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
    coords = []
    url = 'http://locations.crackerbarrel.com/sitemap.xml.gz'
    with open('sitemap.xml.gz','wb') as f:
        f.write(urllib.request.urlopen(url).read())
        f.close()
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    with gzip.open('sitemap.xml.gz', 'rt') as f:
        for line in f:
            if '<loc>http://locations.crackerbarrel.com/' in line:
                lurl = line.replace('/</loc>','</loc>').split('<loc>')[1].split('<')[0]
                if lurl.count('/') == 5 and lurl not in locs:
                    locs.append(lurl)
    print(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        PageFound = True
        while PageFound:
            try:
                PageFound = False
                print(('Pulling Location %s...' % loc))
                url = loc
                add = ''
                city = ''
                state = ''
                zc = ''
                country = 'US'
                phone = ''
                hours = ''
                lat = ''
                lng = ''
                store = loc.rsplit('/',1)[1]
                name = 'Cracker Barrel'
                website = 'crackerbarrel.com'
                typ = 'Restaurant'
                r2 = session.get(loc, headers=headers)
                if r2.encoding is None: r2.encoding = 'utf-8'
                lines = r2.iter_lines(decode_unicode=True)
                Found = False
                for line2 in lines:
                    if 'W2GI.collection.poi = [' in line2:
                        Found = True
                    if Found and 'onlineordering' in line2:
                        Found = False
                    if "name : '" in line2 and Found:
                        name = line2.split("name : '")[1].split("'")[0]
                    if "address1 : '" in line2 and Found:
                        add = line2.split("address1 : '")[1].split("'")[0]
                    if "city : '" in line2 and Found:
                        city = line2.split("city : '")[1].split("'")[0]
                    if "state : '" in line2 and Found:
                        state = line2.split("state : '")[1].split("'")[0]
                    if "postalcode : '" in line2 and Found:
                        zc = line2.split("postalcode : '")[1].split("'")[0]
                    if "latitude : '" in line2 and Found:
                        lat = line2.split("latitude : '")[1].split("'")[0]
                    if "longitude : '" in line2 and Found:
                        lng = line2.split("longitude : '")[1].split("'")[0]
                    if "phone : '" in line2 and Found:
                        phone = line2.split("phone : '")[1].split("'")[0]
                    if "country : '" in line2 and Found:
                        country = line2.split("country : '")[1].split("'")[0]
                    if 'hours" style="display: none;"><span>' in line2:
                        if hours == '':
                            hours = line2.split('hours" style="display: none;"><span>')[1].split('</span></div>')[0].replace('</span>','').replace('<span>','')
                        else:
                            hours = hours + '; ' + line2.split('hours" style="display: none;"><span>')[1].split('</span></div>')[0].replace('</span>','').replace('<span>','')
                if hours == '':
                    hours = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                latlng = lat + '|' + lng
                if latlng not in coords and add != '':
                    coords.append(latlng)
                    yield [website, url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                PageFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
