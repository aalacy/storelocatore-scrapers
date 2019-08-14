import csv
import urllib2
import requests
import json

session = requests.Session()
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
    locs = []
    url = 'https://www.whitecastle.com/sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.whitecastle.com/locations/' in line:
            locs.append(line.split('locations/')[1].split('<')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        lurl = 'https://www.whitecastle.com/wcapi/location-by-store-number?storeNumber=' + loc
        website = 'whitecastle.com'
        name = 'White Castle #' + loc
        store = loc
        hours = ''
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            if '"zip":"' in line2:
                add = line2.split('"address":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split(',"state":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                country = 'US'
                if '"open24x7":true' in line2:
                    hours = 'Open 24 Hours'
                else:
                    hrs = line2.split('"days":[')[1].split(']')[0].split('"},{"')
                    for hr in hrs:
                        day = hr.split('"day":"')[1]
                        if '"open24Hours":false' in hr:
                            time = hr.split('hours":"')[1].split('"')[0]
                        else:
                            time = 'Open 24 Hours'
                        if hours == '':
                            hours = day + ': ' + time
                        else:
                            hours = hours + '; ' + day + ': ' + time
                typ = 'Restaurant'
                lat = line2.split('"lat":"')[1].split('"')[0]
                lng = line2.split('"lng":"')[1].split('"')[0]
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
