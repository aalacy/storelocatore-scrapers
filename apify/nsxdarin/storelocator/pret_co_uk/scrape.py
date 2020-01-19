import csv
import os
import requests
import sgzip
import json

requests.packages.urllib3.disable_warnings()

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['gb'])

MAX_RESULTS = 500

session = requests.Session()

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36'
           }

def fetch_data():
    ids = []
    locations = []
    coord = search.next_coord()
    while coord:
        result_coords = []
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        x, y = coord[0], coord[1]
        url = 'https://www.pret.co.uk/en-gb/find-a-pret/' + str(x) + ',' + str(y)
        r = session.get(url, headers=headers, verify=False)
        lines = r.iter_lines()
        website = 'pret.co.uk'
        typ = 'Restaurant'
        for line in lines:
            if '<div class="panel-heading">' in line:
                hours = ''
                lat = ''
                lng = ''
                add = ''
                city = ''
                state = ''
                zc = ''
                phone = ''
                g = next(lines)
                if '>' in g:
                    name = g.split('>')[1].split('<')[0]
                else:
                    name = next(lines).split('>')[1].split('<')[0]
            if '<address>' in line:
                next(lines)
                g = next(lines)
                h = next(lines)
                i = next(lines)
                j = next(lines)
                k = next(lines)
                if 'United Kingdom ' in k:
                    add = g.strip().replace('\t','').replace('\n','').replace('\r','')
                    add = add + ' ' + h.strip().replace('\t','').replace('\n','').replace('\r','')
                    add = add + ' ' + i.strip().replace('\t','').replace('\n','').replace('\r','')
                    city = j.strip().replace('\t','').replace('\n','').replace('\r','').replace(',','')
                    state = '<MISSING>'
                    zc = k.split('United Kingdom ')[1].strip().replace('\t','').replace('\n','').replace('\r','')
                elif 'United Kingdom' in j:
                    add = g.strip().replace('\t','').replace('\n','').replace('\r','')
                    add = add + ' ' + h.strip().replace('\t','').replace('\n','').replace('\r','')
                    city = i.strip().replace('\t','').replace('\n','').replace('\r','').replace(',','')
                    state = '<MISSING>'
                    zc = j.split('United Kingdom ')[1].strip().replace('\t','').replace('\n','').replace('\r','')
                else:
                    add = g.strip().replace('\t','').replace('\n','').replace('\r','')
                    city = h.strip().replace('\t','').replace('\n','').replace('\r','').replace(',','')
                    state = '<MISSING>'
                    zc = i.split('United Kingdom ')[1].strip().replace('\t','').replace('\n','').replace('\r','')
            if '<div class="map-canvas" data-position="' in line:
                lat = line.split('<div class="map-canvas" data-position="')[1].split(',')[0]
                lng = line.split('<div class="map-canvas" data-position="')[1].split(',')[1].split('"')[0].strip()
            if '<span class="number">Telephone: ' in line:
                phone = line.split('<span class="number">Telephone: ')[1].split('<')[0].strip()
            if '<dt class="opening-hours">' in line:
                day = line.split('<dt class="opening-hours">')[1].split('<')[0]
                g = next(lines)
                if '<dd>' not in g:
                    g = next(lines)
                hrs = day + ': ' + g.split('>')[1].split('<')[0].strip()
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '<div class="directions-panel">' in line:
                loc = '<MISSING>'
                country = 'GB'
                store = '<MISSING>'
                latlng = lat + '|' + lng
                if latlng not in ids:
                    ids.append(latlng)
                    if hours == '':
                        hours = '<MISSING>'
                    if phone == '':
                        phone = '<MISSING>'
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        print("max count update")
        search.max_count_update(result_coords)
        coord = search.next_coord()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
