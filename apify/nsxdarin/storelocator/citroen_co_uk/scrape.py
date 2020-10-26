import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('citroen_co_uk')



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
    url = 'https://www.citroen.co.uk/_/Layout_Citroen_PointsDeVente/getStoreList?lat=51.51&long=-0.13&page=4081&version=129&order=2&area=50000&ztid=&attribut=1000&brandactivity='
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if '"nameAdvisor":"' in item:
                    stub = item.split('"nameAdvisor":"')[1].split('"')[0]
                    locs.append('https://dealer.citroen.co.uk/' + stub)
    for loc in locs:
        logger.info(loc)
        name = ''
        add = ''
        website = 'citroen.co.uk'
        city = ''
        state = ''
        zc = ''
        country = 'GB'
        store = ''
        phone = ''
        typ = ''
        lat = ''
        lng = ''
        HFound = False
        hours = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '"edealerName" : "' in line2:
                name = line2.split('"edealerName" : "')[1].split('"')[0].title().replace('&Amp;','&').replace('&amp;','&')
            if '"brand" : "' in line2:
                typ = line2.split('"brand" : "')[1].split('"')[0].title()
            if '"edealerIDLocal" : "' in line2:
                store = line2.split('"edealerIDLocal" : "')[1].split('"')[0]
            if '"edealerCity" : "' in line2:
                city = line2.split('"edealerCity" : "')[1].split('"')[0].title()
            if '"edealerAddress" : "' in line2:
                add = line2.split('"edealerAddress" : "')[1].split('"')[0].title().replace('&Amp;','&').replace('&amp;','&')
            if '"edealerPostalCode" : "' in line2:
                zc = line2.split('"edealerPostalCode" : "')[1].split('"')[0]
            if '"edealerRegion" : "' in line2:
                state = line2.split('"edealerRegion" : "')[1].split('"')[0].title()
            if '"edealerCountry" : "' in line2:
                country = line2.split('"edealerCountry" : "')[1].split('"')[0].upper()
            if '<h5 class="dealer-header-phone">' in line2 and '</h5>' in line2:
                phone = line2.split('<h5 class="dealer-header-phone">')[1].split('<')[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if '<th colspan="2">Regular Opening Hours</th>' in line2 and hours == '':
                HFound = True
            if HFound and '</table>' in line2:
                HFound = False
            if HFound and 'day</td>' in line2:
                hrs = line2.split('>')[1].split('<')[0] + ': ' + next(lines).split('>')[1].split('<')[0]
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if state == '':
            state = '<MISSING>'
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
