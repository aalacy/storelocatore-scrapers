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
    url = 'https://locations.qdoba.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://locations.qdoba.com/' in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            if lurl.count('/') == 6 and '9258315.html' not in lurl:
                locs.append(lurl)
    print(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        url = loc
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        phone = ''
        hours = ''
        store = ''
        name = 'Qdoba'
        website = 'qdoba.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<!doctype html>' in line2:
                store = line2.split(',"id":')[1].split(',')[0]
                lat = line2.split(',"latitude":')[1].split(',')[0]
                lng = line2.split(',"longitude":')[1].split(',')[0]
                phone = line2.split('itemprop="telephone" id="telephone">')[1].split('<')[0].strip()
                addinfo = line2.split('itemtype="http://schema.org/PostalAddress"')[1].split('</address>')[0]
                add = addinfo.split('<span class="c-address-street-1">')[1].split('<')[0].strip()
                try:
                    add = add + ' ' + addinfo.split('<span class="c-address-street-2">')[1].split('<')[0].strip()
                except:
                    pass
                city = addinfo.split('itemprop="addressLocality">')[1].split('<')[0].strip()
                state = addinfo.split('itemprop="addressRegion">')[1].split('<')[0].strip()
                country = addinfo.split('itemprop="addressCountry">')[1].split('<')[0].strip()
                zc = addinfo.split('itemprop="postalCode">')[1].split('<')[0].strip()
                dayinfo = line2.split("data-days='[")[1].split(']}]')[0]
                days = dayinfo.split('"day":"')
                for day in days:
                    if '"intervals":' in day:
                        if '"end":' not in day:
                            if hours == '':
                                hours = day.split('"')[0] + ': Closed'
                            else:
                                hours = hours + '; ' + day.split('"')[0] + ': Closed'
                        else:
                            if hours == '':
                                hours = day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
                            else:
                                hours = hours + '; ' + day.split('"')[0] + ': ' + day.split('"start":')[1].split('}')[0] + '-' + day.split('"end":')[1].split(',')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
