import csv
import urllib2
import requests

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
    urls = ['https://www.wholefoodsmarket.com/sitemap.xml?page=1','https://www.wholefoodsmarket.com/sitemap.xml?page=2']
    locs = []
    for url in urls:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<loc>https://www.wholefoodsmarket.com/stores/' in line:
                lurl = line.split('<loc>')[1].split('</loc>')[0]
                if lurl not in locs:
                    locs.append(lurl)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        print('Pulling Location %s...' % loc)
        url = loc
        add = ''
        city = ''
        state = ''
        zc = ''
        country = ''
        phone = ''
        hours = ''
        store = '<MISSING>'
        name = 'Whole Foods Market'
        website = 'wholefoodsmarket.com'
        typ = 'Store'
        today = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0].split(' |')[0]
            if "<span class='w-mailing-address-section--description-first'>" in line2:
                add = line2.split("<span class='w-mailing-address-section--description-first'>")[1].split('<')[0]
                csz = line2.split("<span class='w-mailing-address-section--description-last'>")[1].split('<')[0]
                city = csz.split(',')[0]
                state = csz.split(',')[1].strip().split(' ')[0]
                zc = csz.split(',')[1].strip().split(' ',1)[1]
                if ' ' in zc:
                    country = 'CA'
                else:
                    country = 'US'
            if 'class="w-phone-number--link ">' in line2:
                phone = line2.split('class="w-phone-number--link ">')[1].split('<')[0]
            if '<img class="w-map" src=' in line2:
                lat = line2.split('%7C')[1].split(',')[0]
                lng = line2.split('%7C')[1].split(',')[1].split('&')[0]
            if 'Open:</div><div class= "w-hours-of-operation--store-hours w-body-short-form">' in line2:
                today = line2.split('Open:</div><div class= "w-hours-of-operation--store-hours w-body-short-form">')[1].split('<')[0].split(' today')[0]
            if '<div class= "w-hours-of-operation--store-day w-body-short-form">' in line2:
                days = line2.split('<div class= "w-hours-of-operation--store-day w-body-short-form">')
                dnames = []
                for day in days:
                    if '</div>' in day:
                        dname = day.split('</div>')[0]
                        dhrs = day.split('body-short-form">')[1].split('<')[0]
                        dnames.append(dname)
                        if hours == '':
                            hours = dname + ' ' + dhrs
                        else:
                            hours = hours + '; ' + dname + ' ' + dhrs
                alldays = ['Sun:','Mon:','Tue:','Wed:','Thu:','Fri:','Sat:']
                for ditem in alldays:
                    if ditem not in dnames:
                        hours = hours + '; ' + ditem + ' ' + today
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if state == 'BC' or state == 'QC' or state == 'ON':
            country = 'CA'
        if add != '':
            yield [website, url, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
