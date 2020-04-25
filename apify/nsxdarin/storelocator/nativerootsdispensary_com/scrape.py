import csv
import urllib2
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
    for line in r.iter_lines():
        if '<a href="/locations/' in line:
            items = line.split('<a href="/locations/')
            for item in items:
                if '<!DOCTYPE html>' not in item:
                    lurl = item.split('"')[0]
                    if len(lurl) >= 2:
                        locs.append('https://nativerootscannabis.com/locations/' + lurl)
    print('Found %s Locations.' % str(len(locs)))
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
        print('Pulling Location %s...' % loc)
        website = 'nativerootsdispensary.com'
        typ = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<h1 class="css-hcge3v' in line2:
                name = line2.split('<h1 class="css-hcge3v')[1].split('>')[1].split('<')[0]
            if '"@type":"PostalAddress",' in line2 and add == '':
                add = line2.split(',"streetAddress":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
            if '<h5>' in line2:
                typ = line2.split('<h5>')[1].split('</h5>')[0].replace('<i>','').replace('</i>','')
            if '"openingHours":"' in line2 and hours == '':
                hours = line2.split('"openingHours":"')[1].split('"')[0]
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
        if 'eagle-vail-marijuana-CBD-wellness' in loc:
            name = 'Native Roots Wellness CBD Vail'
        phone = phone.replace('+1-','')
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
