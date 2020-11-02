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
    url = 'https://api.storepoint.co/v1/15d97b1ea687fe/locations?lat=41.8265833&long=-72.551402&radius=1000000'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content)['results']['locations']:
        store = item['description']
        name = item['name']
        typ = 'Station'
        website = 'myclarkspns.com'
        lat = item['loc_lat']
        lng = item['loc_long']
        phone = item['phone']
        hours = ''
        purl = '<MISSING>'
        if item['streetaddress'].count(',') == 3 or item['streetaddress'].count(',') >= 5:
            add = item['streetaddress'].split(',')[0]
            city = item['streetaddress'].split(',')[1].strip()
            state = item['streetaddress'].split(',')[2].strip().split(' ')[0]
            zc = item['streetaddress'].split(',')[2].strip().split(' ')[1]
        else:
            add = item['streetaddress'].split(',')[0] + ' ' + item['streetaddress'].split(',')[1]
            city = item['streetaddress'].split(',')[2].strip()
            state = item['streetaddress'].split(',')[3].strip().split(' ')[0]
            zc = item['streetaddress'].split(',')[3].strip().split(' ')[1]
        country = 'US'
        if phone == '':
            phone = '<MISSING>'
        if item['monday'] == '':
            hours = '<MISSING>'
        else:
            hours = 'Mon: ' + item['monday']
            hours = hours + '; Tue: ' + item['tuesday']
            hours = hours + '; Wed: ' + item['wednesday']
            hours = hours + '; Thu: ' + item['thursday']
            hours = hours + '; Fri: ' + item['friday']
            hours = hours + '; Sat: ' + item['saturday']
            hours = hours + '; Sun: ' + item['sunday']
        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
