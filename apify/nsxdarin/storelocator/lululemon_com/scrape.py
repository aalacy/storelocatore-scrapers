import csv
import urllib2
import requests

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://info.lululemon.com/stores?mnid=ftr;en-US;store-locator'
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<h1><a href="/stores/ca/' in line or '<h1><a href="/stores/us/' in line:
            lurl = 'https://shop.lululemon.com' + line.split('href="')[1].split('"')[0]
            locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        print('Pulling Location %s...' % loc)
        website = 'lululemon.com'
        typ = 'Store'
        hours = ''
        store = '<MISSING>'
        locurl = 'https://digcore-store-srvc-prod-blue.lllapi.com/v1/stores?filter=(website_url==' + loc + ')%3B&include=images,spaces,spaces.images'
        headers2 = {'authority': 'digcore-store-srvc-prod-blue.lllapi.com',
                   'scheme': 'https',
                   'method': 'get',
                   'cache-control': 'max-age=0',
                   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
                   }
        r2 = session.get(locurl, headers=headers2)
        for line2 in r2.iter_lines():
            if '"address1":"' in line2:
                add = line2.split('"address1":"')[1].split('"')[0]
                if '"address2":null' not in line2:
                    add = add + ' ' + line2.split('"address2":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                country = line2.split('"country":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(',')[0]
                lng = line2.split('"longitude":')[1].split(',')[0]
                name = line2.split('"name":"')[1].split('"')[0]
                try:
                    phone = line2.split('"phone":"')[1].split('"')[0]
                except:
                    phone = '<MISSING>'
                zc = line2.split('"postal_code":"')[1].split('"')[0]
                state = line2.split('state":"')[1].split('"')[0]
                store = line2.split('"store_number":"')[1].split('"')[0]
                if '"monday":{"close":null' not in line2:
                    if hours == '':
                        hours = 'Mon: ' + line2.split('"monday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"monday":{')[1].split('"close":"')[1].split('"')[0]
                    else:
                        hours = line2.split('"monday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"monday":{')[1].split('"close":"')[1].split('"')[0]
                if '"tuesday":{"close":null' not in line2:
                    if hours == '':
                        hours = 'Tue: ' + line2.split('"tuesday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"tuesday":{')[1].split('"close":"')[1].split('"')[0]
                    else:
                        hours = hours + '; Tue: ' + line2.split('"tuesday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"tuesday":{')[1].split('"close":"')[1].split('"')[0]
                if '"wednesday":{"close":null' not in line2:
                    if hours == '':
                        hours = 'Wed: ' + line2.split('"wednesday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"wednesday":{')[1].split('"close":"')[1].split('"')[0]
                    else:
                        hours = hours + '; Wed: ' + line2.split('"wednesday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"wednesday":{')[1].split('"close":"')[1].split('"')[0]
                if '"thursday":{"close":null' not in line2:
                    if hours == '':
                        hours = 'Thu: ' + line2.split('"thursday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"thursday":{')[1].split('"close":"')[1].split('"')[0]
                    else:
                        hours = hours + '; Thu: ' + line2.split('"thursday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"thursday":{')[1].split('"close":"')[1].split('"')[0]
                if '"friday":{"close":null' not in line2:
                    if hours == '':
                        hours = 'Fri: ' + line2.split('"friday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"friday":{')[1].split('"close":"')[1].split('"')[0]
                    else:
                        hours = hours + '; Fri: ' + line2.split('"friday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"friday":{')[1].split('"close":"')[1].split('"')[0]
                if '"saturday":{"close":null' not in line2:
                    if hours == '':
                        hours = 'Sat: ' + line2.split('"saturday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"saturday":{')[1].split('"close":"')[1].split('"')[0]
                    else:
                        hours = hours + '; Sat: ' + line2.split('"saturday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"saturday":{')[1].split('"close":"')[1].split('"')[0]
                if '"sunday":{"close":null' not in line2:
                    if hours == '':
                        hours = 'Sun: ' + line2.split('"sunday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"sunday":{')[1].split('"close":"')[1].split('"')[0]
                    else:
                        hours = hours + '; Sun: ' + line2.split('"sunday":{')[1].split('"open":"')[1].split('"')[0] + '-' + line2.split('"sunday":{')[1].split('"close":"')[1].split('"')[0]
                if hours == '':
                    hours = '<MISSING>'
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
