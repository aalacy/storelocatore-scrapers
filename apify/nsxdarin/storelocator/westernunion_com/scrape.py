import csv
import urllib2
from sgrequests import SgRequests
import gzip
import os

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
    for x in range(1, 15):
        print('Pulling Sitemap %s...' % str(x))
        smurl = 'http://locations.westernunion.com/sitemap-' + str(x) + '.xml.gz'
        with open('branches.xml.gz','wb') as f:
            f.write(urllib2.urlopen(smurl).read())
            f.close()
            with gzip.open('branches.xml.gz', 'rb') as f:
                for line in f:
                    if '<loc>http://locations.westernunion.com/us/' in line:
                        locs.append(line.split('<loc>')[1].split('<')[0])
        print(str(len(locs)) + ' Locations Found...')
    for loc in locs:
        website = 'westernunion.com'
        typ = 'Location'
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
        store = loc.rsplit('/',1)[1]
        print('Pulling Location %s...' % loc)
        r = session.get(loc, headers=headers)
        lines = r.iter_lines()
        AFound = False
        for line in lines:
            if '"name":"' in line:
                name = line.split('"name":"')[1].split('"')[0]
            if '"streetAddress":"' in line and AFound is False:
                AFound = True
                add = line.split('"streetAddress":"')[1].split('"')[0]
            if '"city":"' in line:
                city = line.split('"city":"')[1].split('"')[0]
            if '"state":"' in line:
                state = line.split('"state":"')[1].split('"')[0]
            if '"postal":"' in line:
                zc = line.split('"postal":"')[1].split('"')[0]
            if '"geoQualitySort":' in line:
                phone = line.split('"geoQualitySort":')[1].split('"phone":"')[1].split('"')[0]
            if '"latitude":' in line:
                lat = line.split('"latitude":')[1].split(',')[0]
            if '"longitude":' in line:
                lng = line.split('"longitude":')[1].split(',')[0]
            if '"monCloseTime":"' in line:
                hours = 'Mon: ' + line.split('"monOpenTime":"')[1].split('"')[0] + '-' + line.split('"monCloseTime":"')[1].split('"')[0]
                hours = hours + '; Tue: ' + line.split('"tueOpenTime":"')[1].split('"')[0] + '-' + line.split('"tueCloseTime":"')[1].split('"')[0]
                hours = hours + '; Wed: ' + line.split('"wedOpenTime":"')[1].split('"')[0] + '-' + line.split('"wedCloseTime":"')[1].split('"')[0]
                hours = hours + '; Thu: ' + line.split('"thuOpenTime":"')[1].split('"')[0] + '-' + line.split('"thuCloseTime":"')[1].split('"')[0]
                hours = hours + '; Fri: ' + line.split('"friOpenTime":"')[1].split('"')[0] + '-' + line.split('"friCloseTime":"')[1].split('"')[0]
                hours = hours + '; Sat: ' + line.split('"satOpenTime":"')[1].split('"')[0] + '-' + line.split('"satCloseTime":"')[1].split('"')[0]
                hours = hours + '; Sun: ' + line.split('"sunOpenTime":"')[1].split('"')[0] + '-' + line.split('"sunCloseTime":"')[1].split('"')[0]
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
