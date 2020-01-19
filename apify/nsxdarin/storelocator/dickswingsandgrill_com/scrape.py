# -*- coding: cp1252 -*-
import csv
import urllib2
import requests
import re

requests.packages.urllib3.disable_warnings()

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://dickswingsandgrill.com/'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    Found = False
    for line in r.iter_lines():
        if 'LOCATIONS</span></a>' in line:
            Found = True
        if Found and '>CONTACT</span>' in line:
            Found = False
        if Found and '"><a href="' in line and '#locations' not in line:
            lurl = line.split('href="')[1].split('"')[0]
            if 'http' in lurl:
                locs.append(lurl)
            else:
                locs.append('https://dickswingsandgrill.com' + lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = '<MISSING>'
        lat = ''
        lng = ''
        hours = ''
        country = 'US'
        zc = ''
        phone = ''
        print('Pulling Location %s...' % loc)
        website = 'dickswingsandgrill.com'
        typ = 'Restaurant'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<title>' in line2:
                name = line2.split('<title>')[1].split(' |')[0]
            if '<h2>' in line2 and '<h2><' not in line2 and 'Weekly' not in line2:
                add = line2.split('<h2>')[1].split('•')[0]
                phone = '(' + line2.split('(')[1].split('<')[0].strip()
            if '!2d-' in line2:
                lng = line2.split('!2d')[1].split('!')[0]
                lat = line2.split('!2d-')[1].split('!3d')[1].split('!')[0]
                try:
                    city = line2.split('%2C+')[1].replace('+',' ')
                    state = line2.split('%2C+')[2].split('+')[0]
                    zc = line2.split('%2C+')[2].split('+')[1].split('!')[0]
                except:
                    city = line2.split('%2C%20')[1].replace('+',' ')
                    state = line2.split('%2C%20')[2].split('%')[0]
                    zc = line2.split('%2C%20')[2].split('%20')[1].split('!')[0]
            if '&#8211;' in line2 and '</span>' not in line2:
                hrs = line2.replace('\r','').replace('\n','').replace('\t','').replace('<strong>','').replace('</strong>','').replace('&#8211;','-').replace('<p style="text-align: right;">','').strip()
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if 'pm<' in line2 and 'wrapper' not in line2:
                hrs = line2.replace('\r','').replace('\n','').replace('\t','').replace('<strong>','').replace('</strong>','').replace('&#8211;','-').replace('<p style="text-align: right;">','').strip()
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if 'CLOSED<' in line2:
                hrs = line2.replace('\r','').replace('\n','').replace('\t','').replace('<strong>','').replace('</strong>','').replace('&#8211;','-').replace('<p style="text-align: right;">','').strip()
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '<p><strong>MON-SUN:<br />' in line2:
                hours = 'MON-SUN: ' + next(lines).split('strong>')[1].split('<')[0].replace('&#8211;','-')                    
        if '•' in add:
            add = add.split('•')[0].strip()
        if phone == '':
            phone = '<MISSING>'
        if zc == '':
            zc = '<MISSING>'
        if add == '':
            add = '<MISSING>'
        if city == '':
            city = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if lat == '':
            lat = '<MISSING>'
        if lng == '':
            lng = '<MISSING>'
        if state == '':
            state = 'FL'
        hours = hours.replace('<br />','').replace('</p>','')
        if 'pm' not in hours.lower():
            hours = '<MISSING>'
        if '(' in add:
            add = add.split('(')[0].strip()
        if '·' in add:
            add = add.split('·')[0].strip()
        add = add.replace('Â â€¢Â','').replace('Â â€¢','').strip()
        if 'Â' in add:
            add = add.split('Â')[0].strip()
        cleanr = re.compile('<.*?>')
        hours = re.sub(cleanr, '', hours)
        if hours == '':
            hours = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
