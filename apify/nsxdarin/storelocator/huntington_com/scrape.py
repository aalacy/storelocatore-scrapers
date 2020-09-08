import csv
import urllib3
from sgrequests import SgRequests
import json

requests.packages.urllib3.disable_warnings()

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.huntington.com/~/media/SEO_Files/sitemap'
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    locs = []
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://www.huntington.com/Community/branch-info?locationId=' in line:
            locs.append(line.split('>')[1].split('<')[0])
    for loc in locs:
        r2 = session.get(loc, headers=headers, verify=False)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        hours = ''
        typ = 'Branch'
        website = 'huntington.com'
        Found = False
        for line2 in lines:
            if '<h1>' in line2:
                name = line2.split('<h1>')[1].split('<')[0]
            if '"streetAddress":"' in line2:
                store = line2.split('"@id":"https://www.huntington.com/?locationId=')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                country = line2.split('"addressCountry":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(',')[0]
                lng = line2.split('"longitude":')[1].split('}')[0]
                items = line2.split('"dayOfWeek":"http://schema.org/')
            if '<!-- Lobby section-->' in line2:
                Found = True
            if Found and '</div>' in line2:
                Found = False
            if Found and '<br' in line2 and ': ' in line2:
                if hours == '':
                    hours = line2.split('>')[1].replace('\r','').replace('\n','').replace('\t','').strip()
                else:
                    hours = hours + '; ' + line2.split('>')[1].replace('\r','').replace('\n','').replace('\t','').strip()
        if hours != '':
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
