import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('bgca_org')



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
    ids = []
    url = ''
    coords = ['61,-150','65,-150','55,-140','61,-160','65,-160','21,-155']
    for coord in coords:
        lat = coord.split(',')[0]
        lng = coord.split(',')[1]
        url = 'https://bgcaorg-find-a-c-1488560011850.appspot.com//x/v1/clubs/' + lat + '/' + lng + '/1000/'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        for line in r.iter_lines(decode_unicode=True):
            if '"City": "' in line:
                typ = '<MISSING>'
                loc = '<MISSING>'
                hours = '<MISSING>'
                country = ''
                website = 'bgca.org'
                city = line.split('"City": "')[1].split('"')[0]
            if '"ZipCode1": "' in line:
                zc = line.split('"ZipCode1": "')[1].split('"')[0]
            if '"State": "' in line:
                state = line.split('"State": "')[1].split('"')[0]
            if '"Country": "USA"' in line:
                country = 'US'
            if '"PhoneNumber": "' in line:
                phone = line.split('"PhoneNumber": "')[1].split('"')[0]
            if '"lng": ' in line:
                lng = line.split('"lng": ')[1].split(',')[0]
            if '"lat": ' in line:
                lat = line.split('"lat": ')[1].split(',')[0]
            if '"Address1": "' in line:
                add = line.split('"Address1": "')[1].split('"')[0]
            if '"Address2": "' in line:
                add = add + ' ' + line.split('"Address2": "')[1].split('"')[0]
            if '"SiteId": "' in line:
                store = line.split('"SiteId": "')[1].split('"')[0]
            if '"SiteName": "' in line:
                name = line.split('"SiteName": "')[1].split('"')[0]
            if '"Native": "' in line:
                if store not in ids and country == 'US':
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                    ids.append(store)
    for x in range(24, 50):
        for y in range(-66, -126, -1):
            lat = str(x)
            lng = str(y)
            logger.info((str(lat) + ',' + str(lng)))
            url = 'https://bgcaorg-find-a-c-1488560011850.appspot.com//x/v1/clubs/' + lat + '/' + lng + '/100/'
            r = session.get(url, headers=headers)
            if r.encoding is None: r.encoding = 'utf-8'
            for line in r.iter_lines(decode_unicode=True):
                if '"City": "' in line:
                    typ = '<MISSING>'
                    loc = '<MISSING>'
                    hours = '<MISSING>'
                    country = ''
                    website = 'bgca.org'
                    city = line.split('"City": "')[1].split('"')[0]
                if '"ZipCode1": "' in line:
                    zc = line.split('"ZipCode1": "')[1].split('"')[0]
                if '"State": "' in line:
                    state = line.split('"State": "')[1].split('"')[0]
                if '"Country": "USA"' in line:
                    country = 'US'
                if '"PhoneNumber": "' in line:
                    phone = line.split('"PhoneNumber": "')[1].split('"')[0]
                if '"lng": ' in line:
                    lng = line.split('"lng": ')[1].split(',')[0]
                if '"lat": ' in line:
                    lat = line.split('"lat": ')[1].split(',')[0]
                if '"Address1": "' in line:
                    add = line.split('"Address1": "')[1].split('"')[0]
                if '"Address2": "' in line:
                    add = add + ' ' + line.split('"Address2": "')[1].split('"')[0]
                if '"SiteId": "' in line:
                    store = line.split('"SiteId": "')[1].split('"')[0]
                if '"SiteName": "' in line:
                    name = line.split('"SiteName": "')[1].split('"')[0]
                if '"Native": "' in line:
                    if store not in ids and country == 'US':
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
                        ids.append(store)

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
