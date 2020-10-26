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
    for x in range(0, 325, 25):
        print(('Pulling Range %s...' % str(x)))
        try:
            url = 'https://www.getgocafe.com/api/sitecore/locations/getlocationlistvm?q=banner:(code+(GG))&skip=' + str(x) + '&top=25&orderBy=geo.distance(storeCoordinate,%20geography%27POINT(-93.2871%2044.9427)%27)%20asc'
            r = session.get(url, headers=headers, verify=False)
            array = json.loads(r.content)
            for item in array['Locations']:
                website = 'getgocafe.com'
                name = item['StoreDisplayName']
                add = item['Address']['lineOne']
                city = item['Address']['City']
                state = item['Address']['State']['Abbreviation']
                zc = item['Address']['Zip']
                phone = item['TelephoneNumbers'][0]['DisplayNumber']
                hours = 'Sun: ' + item['HoursOfOperation'][0]['HourDisplay']
                hours = hours + '; ' + 'Mon: ' + item['HoursOfOperation'][1]['HourDisplay']
                hours = hours + '; ' + 'Tue: ' + item['HoursOfOperation'][2]['HourDisplay']
                hours = hours + '; ' + 'Wed: ' + item['HoursOfOperation'][3]['HourDisplay']
                hours = hours + '; ' + 'Thu: ' + item['HoursOfOperation'][4]['HourDisplay']
                hours = hours + '; ' + 'Fri: ' + item['HoursOfOperation'][5]['HourDisplay']
                hours = hours + '; ' + 'Sat: ' + item['HoursOfOperation'][6]['HourDisplay']
                country = 'US'
                typ = item['Details']['Type']['Name']
                store = item['Id']
                lat = item['Address']['Coordinates']['Latitude']
                lng = item['Address']['Coordinates']['Longitude']
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        except:
            print('No More Locations Found...')

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
