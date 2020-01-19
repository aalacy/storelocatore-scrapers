import csv
import urllib2
import requests
import json

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
    url = 'https://www.kfc.co.uk/api/store?rpp=all'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['data']:
        name = item['display_name'].encode('utf-8')
        website = 'kfc.co.uk'
        typ = item['type']
        store = item['number']
        hours = ''
        country = 'GB'
        add = item['address']['AddressLine1'].encode('utf-8')
        add2 = item['address']['AddressLine2']
        if add2 is not None:
            add = add + ' ' + add2.encode('utf-8')
        city = item['address']['CityOrTown'].encode('utf-8')
        state = item['address']['County'].encode('utf-8')
        zc = item['address']['PostCode']
        lat = item['latitude']
        lng = item['longitude']
        days = item['opening_hours']
        hours = ''
        for day in days:
            hrs = day['day'] + ': ' + day['open'] + '-' + day['close']
            if hours == '':
                hours = hrs
            else:
                hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        loc = '<MISSING>'
        phone = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
