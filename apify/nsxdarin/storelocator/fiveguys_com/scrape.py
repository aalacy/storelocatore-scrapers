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
    url = 'https://www.fiveguys.com/5gapi/stores/ByDistance?lat=40.7135097&lng=-73.9859414&distance=2500000&secondaryDistance=25000000&lang=en&units=M'
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        store = item['ClientKey']
        name = item['LocationName']
        cs = item['ComingSoon']
        hours = item['Hours']
        phone = item['PhoneNumber']
        add = item['AddressLine1'] + ' ' + item['AddressLine2']
        add = add.strip().replace('<p>','').replace('</p>','').replace('\\n','')
        city = item['City']
        state = item['StateOrProvince']
        zc = item['PostalCode']
        country = item['Country']
        lat = item['Latitude']
        lng = item['Longitude']
        website = 'fiveguys.com'
        typ = 'Restaurant'
        purl = '<MISSING>'
        if 'style' in hours:
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        if hours == '':
            hours = '<MISSING>'
        if city == 'ON':
            state = 'ON'
            city = 'Burlington'
        if lat == '0.0':
            lat = '<MISSING>'
            lng = '<MISSING>'
        if country == 'CA' or country == 'US':
            if cs is not True:
                yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
