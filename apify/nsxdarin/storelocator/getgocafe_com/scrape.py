import csv
import urllib2
import requests

session = requests.Session()
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
        print('Pulling Range %s...' % str(x))
        url = 'https://www.getgocafe.com/api/sitecore/locations/getlocationlistvm?q=banner:(code+(GG))&skip=' + str(x) + '&top=25&orderBy=geo.distance(storeCoordinate,%20geography%27POINT(-93.2871%2044.9427)%27)%20asc'
        r = session.get(url, headers=headers, verify=False)
        for line in r.iter_lines():
            if '"Id":"' in line:
                items = line.split('"Id":"')
                for item in items:
                    if '"StoreDisplayName":"' in item:
                        website = 'getgocafe.com'
                        name = item.split('"StoreDisplayName":"')[1].split(':')[1].split('"')[0].strip()
                        add = item.split('"lineOne":"')[1].split('"')[0]
                        city = item.split('"City":"')[1].split('"')[0]
                        state = item.split(',"Abbreviation":"')[1].split('"')[0]
                        zc = item.split('"Zip":"')[1].split('"')[0]
                        phone = item.split('"DisplayNumber":"')[1].split('"')[0]
                        hours = 'Mon: ' + item.split('"Label":"Mon","')[1].split('"Range":{"Label":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Tue: ' + item.split('"Label":"Tue","')[1].split('"Range":{"Label":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Wed: ' + item.split('"Label":"Wed","')[1].split('"Range":{"Label":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Thu: ' + item.split('"Label":"Thu","')[1].split('"Range":{"Label":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Fri: ' + item.split('"Label":"Fri","')[1].split('"Range":{"Label":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Sat: ' + item.split('"Label":"Sat","')[1].split('"Range":{"Label":"')[1].split('"')[0]
                        hours = hours + '; ' + 'Sun: ' + item.split('"Label":"Sun","')[1].split('"Range":{"Label":"')[1].split('"')[0]
                        country = 'US'
                        typ = item.split('"Details":{"Type":{"Code":"')[1].split('"Name":"')[1].split('"')[0]
                        store = item.split('"StoreDisplayName":"')[1].split(':')[0].strip()
                        lat = item.split('"Latitude":')[1].split(',')[0]
                        lng = item.split('"Longitude":')[1].split('}')[0]
                        yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
