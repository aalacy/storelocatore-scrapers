import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "operating_info", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.t-mobile.com/store-locator-sitemap.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<loc>https://www.t-mobile.com/store-locator/' in line:
            items = line.split('<loc>https://www.t-mobile.com/store-locator/')
            for item in items:
                if '</loc>' in item:
                    lurl = 'https://www.t-mobile.com/store-locator/' + item.split('<')[0]
                    if lurl.count('/') == 6:
                        locs.append(lurl)
    for loc in locs:
        #print('Pulling Location %s...' % loc)
        website = 't-mobile.com'
        state = loc.split('/')[4]
        city = loc.split('/')[5]
        lname = loc.split('/')[6]
        lurl = 'https://onmyj41p3c.execute-api.us-west-2.amazonaws.com/prod/v2.1/getStoreByName?state=' + state + '&city=' + city + '&storeName=' + lname + '&ignoreLoadingBar=undefined'
        typ = '<MISSING>'
        opinfo = '<MISSING>'
        hours = ''
        name = ''
        city = ''
        add = ''
        state = ''
        zc = ''
        country = ''
        store = ''
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            try:
                cc = line2.count('"description":"Store Closed"')
                opinfo = '<MISSING>'
                store = line2.split('"id":"')[1].split('"')[0]
                name = line2.split(',"name":"')[1].split('"')[0]
                typ = line2.split('"type":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                loc = line2.split('"url":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(',')[0]
                lng = line2.split('"longitude":')[1].split(',')[0]
                country = 'US'
                hours = 'Mon: ' + line2.split('"day":"Monday",')[1].split('"opens":"')[1].split('"')[0] + '-' + line2.split('"day":"Monday","')[1].split('"closes":"')[1].split('"')[0]
                hours = hours + '; ' + 'Tue: ' + line2.split('"day":"Tuesday",')[1].split('"opens":"')[1].split('"')[0] + '-' + line2.split('"day":"Tuesday","')[1].split('"closes":"')[1].split('"')[0]
                hours = hours + '; ' + 'Wed: ' + line2.split('"day":"Wednesday",')[1].split('"opens":"')[1].split('"')[0] + '-' + line2.split('"day":"Wednesday","')[1].split('"closes":"')[1].split('"')[0]
                hours = hours + '; ' + 'Thu: ' + line2.split('"day":"Thursday",')[1].split('"opens":"')[1].split('"')[0] + '-' + line2.split('"day":"Thursday","')[1].split('"closes":"')[1].split('"')[0]
                hours = hours + '; ' + 'Fri: ' + line2.split('"day":"Friday",')[1].split('"opens":"')[1].split('"')[0] + '-' + line2.split('"day":"Friday","')[1].split('"closes":"')[1].split('"')[0]
                hours = hours + '; ' + 'Sat: ' + line2.split('"day":"Saturday",')[1].split('"opens":"')[1].split('"')[0] + '-' + line2.split('"day":"Saturday","')[1].split('"closes":"')[1].split('"')[0]
                try:
                    hours = hours + '; ' + 'Sun: ' + line2.split('"day":"Sunday",')[1].split('"opens":"')[1].split('"')[0] + '-' + line2.split('"day":"Sunday","')[1].split('"closes":"')[1].split('"')[0]
                except:
                    hours = hours + '; Sun: Closed'
                if cc == 7:
                    opinfo = 'Store Closed'
            except:
                store = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if store != '<MISSING>':
            yield [website, loc, name, opinfo, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
