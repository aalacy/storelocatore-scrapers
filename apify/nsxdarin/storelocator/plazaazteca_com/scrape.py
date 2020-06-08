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
    locs = []
    url = 'https://plazaazteca.com/locations/'
    r = session.get(url, headers=headers)
    website = 'plazaazteca.com'
    country = 'US'
    for line in r.iter_lines():
        if '<h2 class="elementor-heading-title elementor-size-default"><a href="' in line:
            locs.append(line.split('<h2 class="elementor-heading-title elementor-size-default"><a href="')[1].split('"')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        store = '<MISSING>'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        lat = '<MISSING>'
        lng = '<MISSING>'
        hours = ''
        typ = '<MISSING>'
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<title>' in line2:
                name = line2.split('<title>')[1].split('&')[0].strip()
            if '<div class="elementor-text-editor elementor-clearfix"><p>' in line2 and 'At Plaza' not in line2 and 'We invite' not in line2:
                add = line2.split('<div class="elementor-text-editor elementor-clearfix"><p>')[1].split(',')[0]
                city = line2.split('</p><p>')[1].split(',')[0]
                state = line2.split('</p><p>')[1].split(',')[1].strip()
                zc = line2.split('</p><p>')[1].split(',')[2].strip()
                phone = line2.split('</p><p>')[2].split('<')[0]
            if '<div class="elementor-text-editor elementor-clearfix"><p class="p1">' in line2:
                add = line2.split('<div class="elementor-text-editor elementor-clearfix"><p class="p1">')[1].split('<')[0]
                city = line2.split('15px;">')[1].split(',')[0]
                state = line2.split('15px;">')[2].split(',')[0]
                zc = line2.split('15px;">')[3].split('<')[0]
            if '<span >' in line2 and '<span ><' not in line2:
                g = next(lines)
                if '<p' not in g:
                    g = next(lines)
                if 'font-weight: 500;">' in g:
                    hinfo = g.split('font-weight: 500;">')[1].split('<')[0]
                else:
                    hinfo = g.split('">')[1].split('<')[0]
                hrs = line2.split('<span >')[1].split('<')[0] + ': ' + hinfo
                if hours == '':
                    hours = hrs
                else:
                    hours = hours + '; ' + hrs
            if '<p class="p1">(' in line2:
                phone = line2.split('<p class="p1">(')[1].split('<')[0]
            if '</p' in add:
                add = add.split('<')[0]
            if '1467 N Main St' in add:
                city = 'Suffolk'
                state = 'Virginia'
                zc = '23434'
                phone = '(757) 925-1222'
            if '12428 Warwick Blvd' in add:
                city = 'Newport News'
                state = 'Virginia'
                zc = '23606'
                phone = '(757) 599-6727'
            if 'greenville' in loc:
                add = '400 Greenville Blvd SW'
                city = 'Greenville'
                state = 'North Carolina'
                zc = '27834'
                phone = '(252) 321-8008'
            if 'newington' in loc:
                add = '3260 Berlin Tpke'
                city = 'Newington'
                state = 'Connecticut'
                zc = '06111'
                phone = '860-436-9708'
            if 'www.toroazteca.com' in loc:
                add = '194 Buckland Hills Drive Suite 1052'
                city = 'Manchester'
                state = 'Connecticut'
                zc = '06042'
                phone = '860-648-4454'
                hours = 'Monday - Thursday: 11am - 10pm (Bar Open Late); Friday - Saturday: 11am - 11pm (Bar Open Late); Sunday: 11:30am - 10pm (Bar Open Late)'
            if '<' in name:
                name = name.split('<')[0]
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
