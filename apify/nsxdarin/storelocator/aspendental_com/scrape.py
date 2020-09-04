import csv
import urllib.request, urllib.error, urllib.parse
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
    ids = []
    cities = []
    Found = True
    x = 0
    while Found:
        print(x)
        Found = False
        url = 'https://liveapi.yext.com/v2/accounts/me/answers/vertical/query?v=20190101&api_key=5568aa1809f16997ec2ac0c1ed321f59&jsLibVersion=v0.12.1&sessionTrackingEnabled=true&input=dentist%20near%20me&experienceKey=aspen_dental_answers&version=PRODUCTION&verticalKey=locations&limit=50&offset=' + str(x) + '&queryId=878323fa-cfa8-42f2-836f-975b7b1837b9&locale=en'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"id":"' in line:
                Found = True
                x = x + 50
                items = line.split('"id":"')
                for item in items:
                    if '"website":"' in item:
                        lurl = item.split('"website":"')[1].split(',"covid19InformationUrl":"')[0]
                        if '?' in lurl:
                            lurl = lurl.split('?')[0]
                        if '\\u0026utm_source=' in lurl:
                            lurl = lurl.split('\\u0026utm_source=')[0]
                        locs.append(lurl)
                        print(lurl)
    print(('Found %s Locations...' % str(len(locs))))
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        website = 'aspendental.com'
        typ = 'Office'
        hours = ''
        name = ''
        add = ''
        city = ''
        country = 'US'
        state = ''
        zc = ''
        phone = ''
        store = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        HFound = False
        LocFound = True
        while LocFound:
            try:
                LocFound = False
                r2 = session.get(loc, headers=headers, timeout=5)
                if r2.encoding is None: r2.encoding = 'utf-8'
                for line2 in r2.iter_lines(decode_unicode=True):
                    if '<div class="ssa-office-hours" style="background: #eeeeee;z-index:999999">' in line2:
                        HFound = True
                    if HFound and '<div class="col-sm-8">' in line2:
                        HFound = False
                    if HFound and '<p class="ssa-date">' in line2:
                        hrs = line2.split('<p class="ssa-date">')[1].split('<')[0]
                    if HFound and '<p class="ssa-time">' in line2:
                        hrs = hrs + ': ' + line2.split('<p class="ssa-time">')[1].split('<')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
                    if "'officeName':'" in line2:
                        name = line2.split("'officeName':'")[1].split("'")[0]
                        store = line2.split("'facilityNumber':'")[1].split("'")[0]
                        city = line2.split("'addressLocality':'")[1].split("'")[0]
                        state = line2.split(",'addressRegion':'")[1].split("'")[0]
                        zc = line2.split("'postalCode':'")[1].split("'")[0]
                        add = line2.split(",'streetAddress':'")[1].split("'")[0]
                        phone = line2.split("'telephone':'")[1].split("'")[0]
                    if '" target="_blank">GET DIRECTIONS</a>' in line2:
                        lat = line2.split('" target="_blank">GET DIRECTIONS</a>')[0].rsplit('/',1)[1].split(',')[0]
                        lng = line2.split('" target="_blank">GET DIRECTIONS</a>')[0].rsplit('/',1)[1].split(',')[1]
                if hours == '':
                    hours = '<MISSING>'
                if store not in ids:
                    ids.append(store)
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                LocFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
