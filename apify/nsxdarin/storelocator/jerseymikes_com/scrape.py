import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import sgzip
import json

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
    ids = []
    for code in sgzip.for_radius(200):
        Found = True
        pagenum = 1
        url = 'https://www.jerseymikes.com/locations?search=' + code + '&page=1'
        while Found:
            try:
                print(('Pulling Zip Code %s-%s...' % (code, str(pagenum))))
                Found = False
                r = session.get(url, headers=headers)
                if r.encoding is None: r.encoding = 'utf-8'
                lines = r.iter_lines(decode_unicode=True)
                website = 'jerseymikes.com'
                store = ''
                name = "Jersey Mike's"
                typ = 'Restaurant'
                country = 'US'
                hours = '<MISSING>'
                add = ''
                city = ''
                state = ''
                zc = ''
                phone = ''
                lat = ''
                lng = ''
                for line in lines:
                    if 'rel="next">' in line:
                        Found = True
                        url = line.split('href="')[1].split('"')[0].replace('&amp;','&')
                        pagenum = pagenum + 1
                    if '<span class="addr1" itemprop="streetAddress">' in line:
                        add = line.split('<span class="addr1" itemprop="streetAddress">')[1].split('<')[0]
                    if '<span class="addr2">' in line:
                        add = add + ' ' + line.split('<span class="addr2">')[1].split('<')[0]
                    if 'itemprop="addressLocality">' in line:
                        city = line.split('itemprop="addressLocality">')[1].split('<')[0]
                    if 'itemprop="addressRegion">' in line:
                        state = line.split('itemprop="addressRegion">')[1].split('<')[0]
                    if '"postalCode">' in line:
                        zc = line.split('"postalCode">')[1].split('<')[0]
                    if '><a href="tel:+' in line:
                        phone = line.split('><a href="tel:+')[1].split('"')[0]
                    if 'class="pure-button full-width"' in line:
                        if 'https://www.jerseymikes.com/' in line:
                            store = line.split('<a href="https://www.jerseymikes.com/')[1].split('/')[0]
                            country = 'US'
                        else:
                            store = line.split('<a href="https://www.jerseymikes.ca/')[1].split('/')[0]
                            country = 'CA'
                    if '<a href="https://www.google.com/maps/dir/Current+Location/' in line:
                        lat = line.split('<a href="https://www.google.com/maps/dir/Current+Location/')[1].split(',')[0]
                        lng = line.split('<a href="https://www.google.com/maps/dir/Current+Location/')[1].split(',')[1].split('"')[0]
                    if '<div class="location-hours">' in line:
                        hours = line.split('<div class="location-hours">')[1].split('</div>')[0].replace('<br><strong>','; ').replace('</strong>','').replace('<strong>','')
                    if 'More Detail</a>' in line:
                        if store not in ids:
                            ids.append(store)
                            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                Found = False

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
