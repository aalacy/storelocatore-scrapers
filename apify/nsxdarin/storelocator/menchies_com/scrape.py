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
    url = 'https://www.menchies.com/all-locations'
    locs = []
    alllocs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    country = 'US'
    for line in r.iter_lines(decode_unicode=True):
        if '<div class="loc-name"><span class="font-purple title-case"><a href="' in line:
            items = line.split('<div class="loc-name"><span class="font-purple title-case"><a href="')
            for item in items:
                if 'name">Canada' in item:
                    country = 'CA'
                if '<div class="country-wrapper country1">' not in item and country != 'AU':
                    lurl = 'https://www.menchies.com' + item.split('"')[0]
                    if lurl not in alllocs:
                        alllocs.append(lurl)
                        locs.append(lurl + '|' + country)
                if 'name">Australia</h3>' in item:
                    country = 'AU'
    print(('Found %s Locations.' % str(len(locs))))
    for loc in locs:
        name = ''
        add = ''
        country = loc.split('|')[1]
        lurl = loc.split('|')[0]
        lat = ''
        lng = ''
        hours = ''
        store = ''
        city = ''
        state = ''
        zc = ''
        phone = '<MISSING>'
        print(('Pulling Location %s...' % lurl))
        website = 'menchies.com'
        typ = '<MISSING>'
        r2 = session.get(lurl, headers=headers, verify=False)
        if r2.encoding is None: r2.encoding = 'utf-8'
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<h1 class="h2">' in line2:
                name = line2.split('<h1 class="h2">')[1].split('<')[0]
            if '<em class="fa fa-map show-phone info-fa"></em>' in line2:
                addinfo = line2.split('<em class="fa fa-map show-phone info-fa"></em>')[1].split('</strong>')[0]
                if addinfo.count('<br />') == 2:
                    add = addinfo.split('<br />')[0] + ' ' + addinfo.split('<br />')[1]
                    city = addinfo.split('<br />')[2].split(',')[0]
                    state = addinfo.split('<br />')[2].split(',')[1].strip().split(' ')[0]
                    try:
                        zc = addinfo.split('<br />')[2].split(',')[1].strip().split(' ',1)[1]
                    except:
                        zc = '<MISSING>'
                if addinfo.count('<br />') == 1:
                    add = addinfo.split('<br />')[0]
                    city = addinfo.split('<br />')[1].split(',')[0]
                    state = addinfo.split('<br />')[1].split(',')[1].strip().split(' ')[0]
                    try:
                        zc = addinfo.split('<br />')[1].split(',')[1].strip().split(' ',1)[1]
                    except:
                        zc = '<MISSING>'
                if addinfo.count('<br />') == 3:
                    add = addinfo.split('<br />')[0] + ' ' + addinfo.split('<br />')[1]
                    city = addinfo.split('<br />')[3].split(',')[0]
                    state = addinfo.split('<br />')[3].split(',')[1].strip().split(' ')[0]
                    try:
                        zc = addinfo.split('<br />')[3].split(',')[1].strip().split(' ',1)[1]
                    except:
                        zc = '<MISSING>'
                if ' ' in zc:
                    country = 'CA'
                else:
                    country = 'US'
            if '<a href="tel' in line2:
                phone = line2.split('<a href="tel')[1].split('>')[1].split('<')[0]
            if '<p class="loc-hours">' in line2:
                days = line2.split('<p class="loc-hours">')
                for day in days:
                    if 'loc-phone' not in day:
                        if hours == '':
                            hours = day.split('<')[0].strip()
                        else:
                            hours = hours + '; ' + day.split('<')[0].strip()
            if '<span class="favorite fav-' in line2:
                store = line2.split('<span class="favorite fav-')[1].split('"')[0]
            if 'var point = new google.maps.LatLng(' in line2:
                lat = line2.split('var point = new google.maps.LatLng(')[1].split(',')[0]
                lng = line2.split('var point = new google.maps.LatLng(')[1].split(',')[1].split(')')[0].strip()
        yield [website, lurl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
