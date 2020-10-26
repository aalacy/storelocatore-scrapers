# -*- coding: cp1252 -*-
import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    url = 'https://nativerootscannabis.com/locations/'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<a href="/locations/' in line:
            items = line.split('<a href="/locations/')
            for item in items:
                if '<!DOCTYPE html>' not in item:
                    lurl = item.split('"')[0]
                    if len(lurl) >= 2:
                        locs.append('https://nativerootscannabis.com/locations/' + lurl)
    print(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        name = ''
        add = ''
        city = ''
        state = ''
        store = '<MISSING>'
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = ''
        country = 'US'
        zc = ''
        phone = ''
        print(('Pulling Location %s...' % loc))
        website = 'nativerootsdispensary.com'
        typ = ''
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<h1 class="css-hcge3v' in line2:
                name = line2.split('<h1 class="css-hcge3v')[1].split('>')[1].split('<')[0]
            if 'Address</h3><p>' in line2 and '<b>OPENING SOON</b>' not in line2:
                add = line2.split('Address</h3><p>')[1].split('<')[0]
                csz = line2.split('Address</h3><p>')[1].replace('</p><p>','<br/>').split('<hr/>')[0].split('<br/>')[1]
                try:
                    city = csz.split(',')[0]
                    state = csz.split(',')[1].strip().split(' ')[0]
                    zc = csz.split(',')[1].rsplit(' ',1)[1]
                except:
                    city = ''
                    state = ''
                    zc = ''
            if '<b>Address</b></h3>' in line2 and '<b>OPENING SOON</b>' not in line2:
                add = line2.split('Address</b></h3><p>')[1].split('<')[0]
                csz = line2.split('Address</b></h3><p>')[1].replace('</p><p>','<br/>').split('<hr/>')[0].split('<br/>')[1]
                try:
                    city = csz.split(',')[0]
                    state = csz.split(',')[1].strip().split(' ')[0]
                    zc = csz.split(',')[1].rsplit(' ',1)[1]
                except:
                    city = ''
                    state = ''
                    zc = ''
            if '<h3>Phone</h3><p>' in line2:
                phone = line2.split('<h3>Phone</h3><p>')[1].split('<')[0]
            if '<h5>' in line2:
                typ = line2.split('<h5>')[1].split('</h5>')[0].replace('<i>','').replace('</i>','')
            if '"openingHours":"' in line2 and hours == '':
                hours = line2.split('"openingHours":"')[1].split('"')[0]
        typ = typ.replace('Â','')
        if 'broadway' in loc:
            hours = 'Mo, Tu, We, Th, Fr, Sa, Su, 10:00-19:00'
        if 'tower-road' in loc:
            add = '7050 Tower Rd'
            city = 'Denver'
            state = 'CO'
            zc = '80249'
            country = 'US'
            phone = '720-428-8990'
            hours = 'Mo, Tu, We, Th, Fr, Sa, Su, 8:00-22:00'
        if 'champa-wellness-hemp-cbd' in loc:
            name = 'Native Roots Wellness CBD Champa'
            phone = '303-623-1900'
            add = '1555 Champa St'
            city = 'Denver'
            state = 'CO'
            zc = '80202'
            phone = '303-623-1900'
            hours = 'Monday 10am-8pm; Tuesday 10am-8pm; Wednesday 10am-8pm; Thursday 10am-8pm; Friday 10am-9pm; Saturday 10am-9pm; Sunday 10am-8pm'
        if 'eagle-vail-marijuana-CBD-wellness' in loc:
            name = 'Native Roots Wellness CBD Vail'
        phone = phone.replace('+1-','')
        if 'uintah-marijuana-dispensary-and-CBD-wellness' in loc:
            add = '1705 W Uintah St'
            city = 'Colorado Springs'
            state = 'CO'
            zc = '80904'
            phone = '719-375-5512'
            hours = 'Mo, Tu, We, Th, Fr, Sa, Su, 9:00-21:00'
        if 'eagle-vail-marijuana-CBD-wellness' in loc:
            add = '141 E Meadow Dr. Suite #202'
            city = 'Vail'
            state = 'CO'
            zc = '81657'
            phone = '970-470-4572'
            hours = 'Mo, Tu, We, Th, Fr, Sa, Su, 9:00-22:00'
        if 'tejon-marijuana-dispensary-and-CBD-wellness' in loc:
            phone = '719-434-7739'
        if '<' in zc:
            zc = zc.split('<')[0]
        if 'santa-fe-south-denver-marijuana-dispensary' in loc:
            city = 'Denver'
            state = 'CO'
            zc = '80223'
            phone = '720-428-8050'
            hours = 'Mo, Tu, We, Th, Fr, Sa, Su, 9:00-22:00'
        if 'dandelion-boulder-marijuana-dispensary' in loc:
            hours = 'Mo, Tu, We, Th, Fr, Sa, Su, 10:00-19:50'
        if 'edgewater-marijuana-dispensary' in loc:
            hours = 'Mo, Tu, We, Th, Fr, Sa, Su, 9:00-22:00'
        if 'colorado-blvd-marijuana-dispensary' in loc:
            hours = 'Mo, Tu, We, Th, Fr, Sa, Su, 9:00-22:00'
        if city != '':
            if phone == '':
                phone = '<MISSING>'
            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
