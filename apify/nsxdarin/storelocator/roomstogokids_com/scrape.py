import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    locs = []
    links = []
    url = 'https://www.roomstogo.com/stores'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '<div class="link-container"><a href="' in line:
            items = line.split('<div class="link-container"><a href="')
            for item in items:
                if 'Rooms To Go Store Locator' not in item:
                    locs.append('https://www.roomstogo.com' + item.split('"')[0])
    for loc in locs:
        print(('Pulling Location %s...' % loc))
        rs = session.get(loc, headers=headers)
        website = 'roomstogo.com'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        hours = ''
        country = 'US'
        store = ''
        lat = ''
        lng = ''
        for line2 in rs.iter_lines(decode_unicode=True):
            if '<link as="fetch" rel="preload" href="' in line2:
                link = 'https://www.roomstogo.com' + line2.split('<link as="fetch" rel="preload" href="')[1].split('"')[0]
                rl = session.get(link, headers=headers)
                for line3 in rl.iter_lines(decode_unicode=True):
                    if ',"storeNumber":' in line3:
                        store = line3.split(',"storeNumber":')[1].split(',')[0]
                        name = line3.split('"pageTitle":"')[1].split('"')[0]
                        phone = line3.split('"phoneNumber":"')[1].split('"')[0]
                        typ = line3.split('"storeType":"')[1].split('"')[0]
                        try:
                            lat = line3.split('"latitude\\": \\"')[1].split('\\')[0]
                        except:
                            lat = line3.split('"lat":')[1].split(',')[0]
                        try:
                            lng = line3.split('"longitude\\": \\"')[1].split('\\')[0]
                        except:
                            lng = line3.split('"lon":')[1].split('}')[0]
                        try:
                            add = line3.split('"streetAddress\\": \\"')[1].split('\\')[0]
                        except:
                            add = line3.split('"address1":"')[1].split('"')[0]
                        try:
                            city = line3.split('"addressLocality\\": \\"')[1].split('\\')[0]
                        except:
                            city = line3.split('"city":"')[1].split('"')[0]
                        try:
                            state = line3.split('"addressRegion\\": \\"')[1].split('\\')[0]
                        except:
                            state = line3.split('"state":"')[1].split('"')[0]
                        try:
                           zc = line3.split('"postalCode\\": \\"')[1].split('\\')[0]
                        except:
                            zc = line3.split('"zip":"')[1].split('"')[0]
                        hours = 'Mon: ' + line3.split('{"mondayOpen":"')[1].split('"')[0] + '-' + line3.split('"mondayClosed":"')[1].split('"')[0]
                        hours = hours + '; Tue: ' + line3.split('"tuesdayOpen":"')[1].split('"')[0] + '-' + line3.split('"tuesdayClosed":"')[1].split('"')[0]
                        hours = hours + '; Wed: ' + line3.split('"wednesdayOpen":"')[1].split('"')[0] + '-' + line3.split('"wednesdayClosed":"')[1].split('"')[0]
                        hours = hours + '; Thu: ' + line3.split('"thursdayOpen":"')[1].split('"')[0] + '-' + line3.split('"thursdayClosed":"')[1].split('"')[0]
                        hours = hours + '; Fri: ' + line3.split('"fridayOpen":"')[1].split('"')[0] + '-' + line3.split('"fridayClosed":"')[1].split('"')[0]
                        hours = hours + '; Sat: ' + line3.split('"saturdayOpen":"')[1].split('"')[0] + '-' + line3.split('"saturdayClosed":"')[1].split('"')[0]
                        hours = hours + '; Sun: ' + line3.split('"sundayOpen":"')[1].split('"')[0] + '-' + line3.split('"sundayClosed":"')[1].split('"')[0]
                        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
