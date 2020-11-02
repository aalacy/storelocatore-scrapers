import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

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
    url = 'https://api.sofology.co.uk/api/store/'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        website = 'sofology.co.uk'
        name = item['outlet']
        store = item['id']
        try:
            add = item['addressOne'] + ' ' + item['addressTwo']
        except:
            add = item['addressOne']
        zc = item['postCode']
        state = '<MISSING>'
        city = item['town']
        country = 'GB'
        phone = item['phone']
        hours = item['openingTimes'].replace('</li><li>','; ').replace('<li>','').replace('<span>','').replace('</li>','').replace('</span>','').replace('  ',' ')
        purl = 'https://www.sofology.co.uk/stores/' + name.lower().replace(' ','-')
        lat = item['lat']
        lng = item['lng']
        typ = '<MISSING>'
        if name == 'Croydon':
            city = 'Croydon'
        if name == 'Blackburn':
            hours = 'Mon - Fri: 10am - 8pm; Saturday:10am - 6pm; Sunday: 11am - 5pm'
        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
