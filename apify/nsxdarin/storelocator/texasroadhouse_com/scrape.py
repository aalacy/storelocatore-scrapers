import csv
from sgrequests import SgRequests
import json

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
    url = 'https://www.texasroadhouse.com/sitemap.xml'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '<loc>https://www.texasroadhouse.com/locations/' in line and '/intl' not in line:
            lurl = line.split('<loc>')[1].split('<')[0]
            locs.append(lurl)
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        print(loc)
        name = ''
        add = ''
        website = 'texasroadhouse.com'
        country = 'US'
        add = ''
        store = '<MISSING>'
        city = ''
        typ = '<MISSING>'
        state = ''
        zc = ''
        lat = ''
        lng = ''
        phone = ''
        hours = ''
        for line2 in r2.iter_lines():
            line2 = str(line2.decode('utf-8'))
            if 'itemprop="name">' in line2:
                name = line2.split('itemprop="name">')[1].split('<')[0]
            if '"address1":"' in line2:
                add = line2.split('"address1":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                lat = line2.split('"gps_lat":')[1].split(',')[0]
                lng = line2.split(',"gps_lon":')[1].split(',')[0]
                days = line2.split('"schedule":[')[1].split(']')[0].split('"day":"')
                for day in days:
                    if '"hours":' in day:
                        hrs = day.split('"')[0] + ': ' + day.split('"open":"')[1].split('"')[0] + '-' + day.split('"close":"')[1].split('"')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if add != '':
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
