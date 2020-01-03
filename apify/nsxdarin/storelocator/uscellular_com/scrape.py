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
    locs = []
    url = 'https://uscc.koremuat.com//getStores?callback=jQuery1910010208167602496543_1577813002514&xMin=-179.29488281249996&yMin=10.17114643872303&xMax=-50.37398437499996&yMax=69.32114216809255&zoom=20&deltaX=3.955078125&deltaY=3.1724993594054274&stores=9&buffer=9&offset=0&filters=on%2C&retailers=&paymentTypes=&closestPOI=&_=1577813002518'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if ',"id":' in line:
            items = line.split(',"id":')
            for item in items:
                if 'jQuery' not in item:
                    locs.append(item.split(',')[0])
    for loc in locs:
        print('Pulling Location %s...' % loc)
        lurl = 'https://uscc.koremuat.com//getStoreInfo?callback=jQuery191011573511012738757_1577812759166&id=' + loc
        website = 'uscellular.com'
        typ = '<MISSING>'
        hours = ''
        name = ''
        add = ''
        city = ''
        store = ''
        state = ''
        zc = ''
        country = 'US'
        phone = ''
        lat = ''
        lng = ''
        r2 = session.get(lurl, headers=headers)
        for line2 in r2.iter_lines():
            if '"success":true' in line2:
                zc = line2.split('"zip":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                add = line2.split(',"address":"')[1].split('"')[0]
                name = line2.split('"title":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                hours = line2.split('hours":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(',')[0]
                lng = line2.split('"longitude":')[1].split(',')[0]
                store = line2.split('"storeId":"')[1].split('"')[0]
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        purl = '<MISSING>'
        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
