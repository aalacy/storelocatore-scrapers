import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import gzip
import os
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('westernunion_ca')



session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    for x in range(1, 5):
        #logger.info(('Pulling Sitemap %s...' % str(x)))
        smurl = 'http://locations.westernunion.com/sitemap-' + str(x) + '.xml.gz'
        with open('branches.xml.gz','wb') as f:
            f.write(urllib.request.urlopen(smurl).read())
            f.close()
            with gzip.open('branches.xml.gz', 'rt') as f:
                for line in f:
                    if '<loc>http://locations.westernunion.com/ca/' in line:
                        locs.append(line.split('<loc>')[1].split('<')[0])
        #logger.info((str(len(locs)) + ' Locations Found...'))
    for loc in locs:
        website = 'westernunion.ca'
        typ = '<MISSING>'
        store = '<MISSING>'
        hours = '<MISSING>'
        city = ''
        add = ''
        state = ''
        zc = ''
        if '/us/' in loc:
            country = 'US'
        if '/ca/' in loc:
            country = 'CA'
        name = ''
        phone = ''
        lat = ''
        lng = ''
        r = session.get(loc, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        lines = r.iter_lines(decode_unicode=True)
        AFound = False
        for line in lines:
            if '<h1 class="wu_LocationCard' in line:
                name = line.split('<h1 class="wu_LocationCard')[1].split('">')[1].split('<')[0]
                if 'Western Union Agent Location' in name:
                    name = name.replace(name[:32], '')
                    name = name.strip()
            if '"streetAddress":"' in line and AFound is False:
                AFound = True
                add = line.split('"streetAddress":"')[1].split('"')[0]
                state = line.split('"state":"')[1].split('"')[0]
                city = line.split('"city":"')[1].split('"')[0]
                zc = line.split('"postal":"')[1].split('"')[0]
                lat = line.split('"latitude":')[1].split(',')[0]
                lng = line.split('"longitude":')[1].split(',')[0]
                if phone == '':
                    phone = line.split('","phone":"')[1].split('"')[0]
                if store == '<MISSING>':
                    store = line.split('"id":"')[1].split('"')[0]
            if '"desktopHours":{"desktopHours":{' in line:
                hours = line.split('"desktopHours":{"desktopHours":{')[1].split('}}')[0]
                hours = hours.replace('","','; ').replace('"','')
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
