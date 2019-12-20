import csv
import urllib2
import requests

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
    url = 'https://www.walmart.com/sitemap_store_main.xml'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        if '<loc>https://www.walmart.com/store/' in line:
            items = line.split('<loc>https://www.walmart.com/store/')
            for item in items:
                if 'details<' in item:
                    lurl = 'https://www.walmart.com/store/' + item.split('<')[0]
                    locs.append(lurl)     
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        store = loc.split('/store/')[1].split('/')[0]
        name = ''
        add = ''
        city = ''
        state = ''
        lat = ''
        lng = ''
        hours = ''
        country = 'US'
        zc = ''
        phone = ''
        print('Pulling Location %s...' % loc)
        website = 'walmart.com'
        typ = 'Store'
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '"storeType":{"id":"' in line2:
                name = line2.split('"storeType":{"id":"')[0].rsplit('"displayName":"',1)[1].split('"')[0]
                phone = line2.split('"storeType":{"id":"')[1].split('"phone":"')[1].split('"')[0]
                add = line2.split('"address":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                hours = 'Mon: ' + line2.split('"storeType":{"id":"')[1].split('"mondayHrs":')[1].split('"startHr":"')[1].split('"')[0] + '-' + line2.split('"storeType":{"id":"')[1].split('"mondayHrs":')[1].split('"endHr":"')[1].split('"')[0]
                hours = hours + '; Tue: ' + line2.split('"storeType":{"id":"')[1].split('"tuesdayHrs":')[1].split('"startHr":"')[1].split('"')[0] + '-' + line2.split('"storeType":{"id":"')[1].split('"tuesdayHrs":')[1].split('"endHr":"')[1].split('"')[0]
                hours = hours + '; Wed: ' + line2.split('"storeType":{"id":"')[1].split('"wednesdayHrs":')[1].split('"startHr":"')[1].split('"')[0] + '-' + line2.split('"storeType":{"id":"')[1].split('"wednesdayHrs":')[1].split('"endHr":"')[1].split('"')[0]
                hours = hours + '; Thu: ' + line2.split('"storeType":{"id":"')[1].split('"thursdayHrs":')[1].split('"startHr":"')[1].split('"')[0] + '-' + line2.split('"storeType":{"id":"')[1].split('"thursdayHrs":')[1].split('"endHr":"')[1].split('"')[0]
                hours = hours + '; Fri: ' + line2.split('"storeType":{"id":"')[1].split('"fridayHrs":')[1].split('"startHr":"')[1].split('"')[0] + '-' + line2.split('"storeType":{"id":"')[1].split('"fridayHrs":')[1].split('"endHr":"')[1].split('"')[0]
                hours = hours + '; Sat: ' + line2.split('"storeType":{"id":"')[1].split('"saturdayHrs":')[1].split('"startHr":"')[1].split('"')[0] + '-' + line2.split('"storeType":{"id":"')[1].split('"saturdayHrs":')[1].split('"endHr":"')[1].split('"')[0]
                hours = hours + '; Sun: ' + line2.split('"storeType":{"id":"')[1].split('"sundayHrs":')[1].split('"startHr":"')[1].split('"')[0] + '-' + line2.split('"storeType":{"id":"')[1].split('"sundayHrs":')[1].split('"endHr":"')[1].split('"')[0]
            if '"geoPoint":{"latitude":' in line2:
                lat = line2.split('"geoPoint":{"latitude":')[1].split(',')[0]
                lng = line2.split('"longitude":')[1].split('}')[0]
            if ',"phone":"' in line2 and phone == '':
                phone = line.split(',"phone":"')[1].split('"')[0]
        if 'Supercenter' in name:
            typ = 'Supercenter'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
