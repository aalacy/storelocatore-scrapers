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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://delivery.panerabread.com/foundation-api/public/search/cafes?longitude=-95&latitude=40&limit=5000&sortOrder=ASC&sortColumn=Distance&radius=38400000&featureProp=%27YES%27&searchRadius=38400000'
    r = session.get(url, headers=headers)
    array = json.loads(r.content)
    for item in array['features']:
        zc = item['properties']['Zip']
        store = item['properties']['CafeId']
        name = 'Panera Bread'
        add = item['properties']['StreetName']
        city = item['properties']['City']
        state = item['properties']['State']
        phone = item['properties']['Phone']
        website = 'panerabread.com'
        typ = 'Restaurant'
        country = item['properties']['locationProperties']['countryCode']
        hrs = item['properties']['Hours']
        hours = 'Sun: ' + hrs.split('"Sun"')[1].split('"open":"')[1].split('"')[0] + '-' + hrs.split('"Sun"')[1].split('"close":"')[1].split('"')[0]
        hours = hours + '; Mon: ' + hrs.split('"Mon"')[1].split('"open":"')[1].split('"')[0] + '-' + hrs.split('"Mon"')[1].split('"close":"')[1].split('"')[0]
        hours = hours + '; Tue: ' + hrs.split('"Tue"')[1].split('"open":"')[1].split('"')[0] + '-' + hrs.split('"Tue"')[1].split('"close":"')[1].split('"')[0]
        hours = hours + '; Wed: ' + hrs.split('"Wed"')[1].split('"open":"')[1].split('"')[0] + '-' + hrs.split('"Wed"')[1].split('"close":"')[1].split('"')[0]
        hours = hours + '; Thu: ' + hrs.split('"Thu"')[1].split('"open":"')[1].split('"')[0] + '-' + hrs.split('"Thu"')[1].split('"close":"')[1].split('"')[0]
        hours = hours + '; Fri: ' + hrs.split('"Fri"')[1].split('"open":"')[1].split('"')[0] + '-' + hrs.split('"Fri"')[1].split('"close":"')[1].split('"')[0]
        hours = hours + '; Sat: ' + hrs.split('"Sat"')[1].split('"open":"')[1].split('"')[0] + '-' + hrs.split('"Sat"')[1].split('"close":"')[1].split('"')[0]
        lat = item['geometry']['coordinates'][0]
        lng = item['geometry']['coordinates'][1]
        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
