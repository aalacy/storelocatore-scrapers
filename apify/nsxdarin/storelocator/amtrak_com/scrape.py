import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('amtrak_com')



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
    canada = ['SK','ON','PQ','QC','AB','MB','BC','YT','NS','NF','NL','PEI','PE']
    url = 'https://www.amtrak.com/sitemap.xml'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<loc>https://www.amtrak.com/stations/' in line:
            items = line.split('<loc>https://www.amtrak.com/stations/')
            for item in items:
                if '<?xml' not in item:
                    lurl = 'https://maps.amtrak.com/services/MapDataService/StationInfo/getStationInfo?stationCode=' + item.split('<')[0]
                    locs.append(lurl)
    for loc in locs:
        logger.info(('Pulling Location %s...' % loc))
        website = 'amtrak.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        country = 'US'
        lat = '<MISSING>'
        lng = '<MISSING>'
        phone = '215-856-7924'
        store = loc.rsplit('=',1)[1]
        lurl = 'https://www.amtrak.com/stations/' + store
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '"name":"' in line2:
                name = line2.split('"name":"')[1].split('"')[0]
            if '"latitude":"' in line2:
                lat = line2.split('"latitude":"')[1].split('"')[0]
            if '"longitude":"' in line2:
                lng = line2.split('"longitude":"')[1].split('"')[0]
            if '"stationType":"' in line2:
                typ = line2.split('"stationType":"')[1].split('"')[0]
            if '"addressLine":["' in line2:
                add = line2.split('"addressLine":["')[1].split('"')[0]
            if '"cityName":"' in line2:
                city = line2.split('"cityName":"')[1].split('"')[0]
            if '"postalCode":"' in line2:
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if '"stateProv":{"stateCode":"' in line2:
                state = line2.split('"stateProv":{"stateCode":"')[1].split('"')[0]
        hurl = 'https://www.amtrak.com/content/amtrak/en-us/stations/bos.stationTabContainer.' + store.upper() + '.json'
        r3 = session.get(hurl, headers=headers)
        if r3.encoding is None: r3.encoding = 'utf-8'
        for line3 in r3.iter_lines(decode_unicode=True):
            if '"type":"stationhours","rangeData":[{' in line3:
                days = line3.split('"type":"stationhours","rangeData":[{')[1].split('}]}]},')[0].split('"day":"')
                for day in days:
                    if 'timeSlot' in day:
                        hrs = day.split('"')[0] + ': ' + day.split('"timeSlot":"')[1].split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if state in canada:
            country = 'CA'
        if add != '':
            yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
