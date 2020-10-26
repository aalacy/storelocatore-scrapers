import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('cariboucoffee_com')



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
    url = 'https://locations.cariboucoffee.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'hreflang="en" href="https://locations.cariboucoffee.com/us/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if lurl.count('/') == 6:
                locs.append(lurl)
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'cariboucoffee.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        state = ''
        city = ''
        add = ''
        zc = ''
        phone = ''
        lat = ''
        lng = ''
        store = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'dimension4":"' in line2:
                name = line2.split('dimension4":"')[1].split('"')[0]
            if '<span class="c-address-street-1">' in line2:
                try:
                    phone = line2.split('itemprop="telephone" id="telephone">')[1].split('<')[0]
                except:
                    phone = '<MISSING>'
                add = line2.split('<span class="c-address-street-1">')[1].split('<')[0]
                city = line2.split('<span class="c-address-city">')[1].split('<')[0]
                country = 'US'
                zc = line2.split('itemprop="postalCode">')[1].split('<')[0]
                state = line2.split('itemprop="addressRegion">')[1].split('<')[0]
                days = line2.split('<td class="c-location-hours-details-row-day">')
                for day in days:
                    if '<td class="c-location-hours-details-row-intervals' in day:
                        dname = day.split('<')[0]
                        hrs = day.split('<td class="c-location-hours-details-row-intervals')[1].split('</td>')[0]
                        if 'Closed' in hrs:
                            hrs = 'Closed'
                        elif '24 hours' in hrs:
                            hrs = 'Open 24 Hours'
                        else:
                            hrs = hrs.split('instance-open">')[1].split('<')[0] + '-' + hrs.split('instance-close">')[1].split('<')[0]
                        if hours == '':
                            hours = dname + ': ' + hrs
                        else:
                            hours = hours + '; ' + dname + ': ' + hrs
            if ', {"ids":' in line2:
                store = line2.split(', {"ids":')[1].split(',')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[0]
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
