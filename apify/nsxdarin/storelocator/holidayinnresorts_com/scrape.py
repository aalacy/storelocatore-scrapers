import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('candlewoodsuites_com')



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
    url = 'https://www.ihg.com/bin/sitemap.holidayinnresorts.en.printfactsheet.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if 'hreflang="en" rel="alternate">' in line:
            locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        Found = False
        website = 'holidayinnresorts.com'
        country = 'US'
        name = ''
        add = ''
        hours = '<MISSING>'
        state = ''
        city = ''
        phone = ''
        lat = ''
        lng = ''
        store = loc.split('/hoteldetail/')[0].rsplit('/',1)[1]
        typ = 'Hotel'
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'class="country"> United States' in line2:
                Found = True
            if '<h1 id="hotelname">' in line2:
                name = line2.split('<h1 id="hotelname">')[1].split('<')[0]
            if '<p>Hotel Front Desk:</p><p>' in line2:
                phone = line2.split('<p>Hotel Front Desk:</p><p>')[1].split('<')[0]
            if '<span class="street">' in line2:
                add = line2.split('title=')[1].split('">')[1].split('<')[0].strip()
            if '<span class="cityStateZip">' in line2:
                csz = line2.split('<span class="cityStateZip">')[1].split('title=')[1].split('">')[1].split('<')[0].strip()
                city = csz.split(',')[0]
                sz = csz.split(',')[1].strip()
                size = len(sz)
                state = sz[:size - 5]
                zc = csz[-5:]
            if '"place:location:latitude"  content="' in line2:
                lat = line2.split('"place:location:latitude"  content="')[1].split('"')[0]
            if '"place:location:longitude" content="' in line2:
                lng = line2.split('"place:location:longitude" content="')[1].split('"')[0]
        if Found:
            loc = loc.replace('/printfactsheet','')
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
