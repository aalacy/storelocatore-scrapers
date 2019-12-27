import csv
import urllib2
import requests
import time

requests.packages.urllib3.disable_warnings()

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'x-frame-options': 'ALLOW-FROM https://www.apply2.pnc.com/',
           'x-xss-protection': '1; mode=block',
           'authority': 'apps.pnc.com',
           'method': 'GET',
           'scheme': 'https',
           'accept': 'application/json, text/plain, */*',
           'x-app-key': 'pyHnMuBXUM1p4AovfkjYraAJp6'
           }

headers2 = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://apps.pnc.com/locator-api/locator/api/v1/locator/browse?t=1575479568229'
    r = session.get(url, headers=headers, verify=False)
    locs = []
    for line in r.iter_lines():
        if '"externalId" : "' in line:
            lid = line.split('" : "')[1].split('"')[0]
            locs.append(lid)
    print('Found %s Locations...' % str(len(locs)))
    for loc in locs:
        PageFound = True
        lurl = 'https://apps.pnc.com/locator-api/locator/api/v2/location/' + loc
        while PageFound:
            try:
                PageFound = False
                r2 = session.get(lurl, headers=headers2, timeout=3, verify=False)
                lines = r2.iter_lines()
                website = 'pnc.com'
                HFound = False
                hours = ''
                TypFound = False
                print('Pulling Location %s...' % loc)
                for line2 in lines:
                    if '"locationName" : "' in line2:
                        name = line2.split('"locationName" : "')[1].split('"')[0]
                    if '"locationTypeDesc" : "' in line2 and TypFound is False:
                        TypFound = True
                        typ = line2.split('"locationTypeDesc" : "')[1].split('"')[0]
                        store = loc
                    if '"address1" : "' in line2:
                        add = line2.split('"address1" : "')[1].split('"')[0]
                    if '"address2" : "' in line2:
                        add = add + ' ' + line2.split('"address2" : "')[1].split('"')[0]
                    if '"city" : "' in line2:
                        city = line2.split('"city" : "')[1].split('"')[0]
                    if '"state" : "' in line2:
                        state = line2.split('"state" : "')[1].split('"')[0]
                    if '"zip" : "' in line2:
                        zc = line2.split('"zip" : "')[1].split('"')[0]
                    if '"latitude" : ' in line2:
                        lat = line2.split('"latitude" : ')[1].split(',')[0]
                    if '"longitude" : ' in line2:
                        lng = line2.split('"longitude" : ')[1].split(',')[0]
                    if '"contactDescriptionDB" : "External Phone",' in line2:
                        phone = next(lines).split(' : "')[1].split('"')[0]
                    if '"serviceNameDB" : "Lobby Hours"' in line2:
                        HFound = True
                    if HFound and '"hoursByDayIndex"' in line2:
                        HFound = False
                    if HFound and 'day"' in line2:
                        day = line2.split('"')[1]
                        g = next(lines)
                        h = next(lines)
                        if 'null' in g:
                            hrs = 'Closed'
                        else:
                            hrs = g.split('"')[3] + '-' + h.split('"')[3]
                        if hours == '':
                            hours = day + ': ' + hrs
                        else:
                            hours = hours + '; ' + day + ': ' + hrs
                country = 'US'
                purl = 'https://apps.pnc.com/locator/#/result-details/' + loc
                if hours == '':
                    hours = '<MISSING>'
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                PageFound = True
            

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
