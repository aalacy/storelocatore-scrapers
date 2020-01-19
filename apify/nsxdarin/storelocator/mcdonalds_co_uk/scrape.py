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
    url = 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=51.52813399999999&longitude=-0.06165120000002844&radius=8045&maxResults=5000&country=gb&language=en-gb&showClosed=&hours24Text=Open%2024%20hr'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['features']:
        name = item['properties']['name']
        add = item['properties']['addressLine1']
        add = add + ' ' + item['properties']['addressLine2']
        add = add.strip()
        country = 'GB'
        city = item['properties']['addressLine3']
        state = '<MISSING>'
        zc = item['properties']['postcode']
        phone = item['properties']['telephone']
        website = 'mcdonalds.co.uk'
        hours = 'Mon: ' + item['properties']['restauranthours']['hoursMonday']
        hours = hours + '; Tue: ' + item['properties']['restauranthours']['hoursTuesday']
        hours = hours + '; Wed: ' + item['properties']['restauranthours']['hoursWednesday']
        hours = hours + '; Thu: ' + item['properties']['restauranthours']['hoursThursday']
        hours = hours + '; Fri: ' + item['properties']['restauranthours']['hoursFriday']
        hours = hours + '; Sat: ' + item['properties']['restauranthours']['hoursSaturday']
        hours = hours + '; Sun: ' + item['properties']['restauranthours']['hoursSunday']
        typ = 'Restaurant'
        loc = '<MISSING>'
        store = item['properties']['identifiers']['storeIdentifier'][1]['identifierValue']
        lat = item['geometry']['coordinates'][0]
        lng = item['geometry']['coordinates'][1]
        if phone == '':
            phone = '<MISSING>'
        if city == '':
            city = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
