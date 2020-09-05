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
    url = 'https://familyexpress.com/api/locations/place'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        website = 'familyexpress.com'
        name = ''
        add = ''
        city = ''
        state = ''
        zc = ''
        phone = ''
        hours = ''
        country = ''
        typ = 'Store'
        store = ''
        lat = ''
        lng = ''
        for line in r.iter_lines(decode_unicode=True):
            if '"updated_at":"' in line:
                items = line.split('"storeId":"')
                for item in items:
                    if '"entityType":"' in item:
                        phone = item.split('"mainPhone":"')[1].split('"')[0]
                        store = item.split('"')[0]
                        name = item.split('"c_subName":"')[1].split('"')[0]
                        add = item.split(',"line1":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"region":"')[1].split('"')[0]
                        zc = item.split('"postalCode":"')[1].split('"')[0]
                        country = item.split('"countryCode":"')[1].split('"')[0]
                        lat = item.split('{"latitude":')[1].split(',')[0]
                        lng = item.split('"longitude":')[1].split('}')[0]
                        hrs = item.split('"hours":')[1].split(']}}')[0]
                        hours = 'Mon: ' + hrs.split('"monday":{"openIntervals":[{"end":"')[1].split('"start":"')[1].split('"')[0] + '-' + item.split('"monday":{"openIntervals":[{"end":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Tue: ' + hrs.split('"tuesday":{"openIntervals":[{"end":"')[1].split('"start":"')[1].split('"')[0] + '-' + item.split('"tuesday":{"openIntervals":[{"end":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Wed: ' + hrs.split('"wednesday":{"openIntervals":[{"end":"')[1].split('"start":"')[1].split('"')[0] + '-' + item.split('"wednesday":{"openIntervals":[{"end":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Thu: ' + hrs.split('"thursday":{"openIntervals":[{"end":"')[1].split('"start":"')[1].split('"')[0] + '-' + item.split('"thursday":{"openIntervals":[{"end":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Fri: ' + hrs.split('"friday":{"openIntervals":[{"end":"')[1].split('"start":"')[1].split('"')[0] + '-' + item.split('"friday":{"openIntervals":[{"end":"')[1].split('"')[0]
                        try:
                            hours = hours + '; ' + 'Sat: ' + hrs.split('"saturday":{"openIntervals":[{"end":"')[1].split('"start":"')[1].split('"')[0] + '-' + item.split('"saturday":{"openIntervals":[{"end":"')[1].split('"')[0]
                        except:
                            hours = hours + '; Sat: Closed'
                        try:
                            hours = hours + '; ' + 'Sun: ' + hrs.split('"sunday":{"openIntervals":[{"end":"')[1].split('"start":"')[1].split('"')[0] + '-' + item.split('"sunday":{"openIntervals":[{"end":"')[1].split('"')[0]
                        except:
                            hours = hours + '; Sun: Closed'
                        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
