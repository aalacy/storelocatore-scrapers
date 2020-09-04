import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import sgzip
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
    ids = []
    for code in sgzip.for_radius(50):
        print(('Pulling Zip Code %s...' % code))
        try:
            url = 'https://savealot.com/grocery-stores/locationfinder/modules/multilocation/?near_location=' + code + '&threshold=4000&services__in=&within_business=true'
            r = session.get(url, headers=headers, verify=False)
            array = json.loads(r.content)['objects']
            for item in array:
                website = 'savealot.com'
                phone = item['phonemap_e164']['phone']
                state = item['state_name']
                store = item['id']
                purl = item['location_url']
                city = item['city']
                name = 'Save A Lot'
                add = item['street']
                zc = item['postal_code']
                country = 'US'
                typ = 'Store'
                lat = item['lat']
                lng = item['lon']
                hrs = item['hours_by_type']['primary']['hours']
                try:
                    hours = 'Mon: ' + hrs[0][0][0] + '-' + hrs[0][0][1]
                    hours = hours + '; ' + 'Tue: ' + hrs[1][0][0] + '-' + hrs[1][0][1]
                    hours = hours + '; ' + 'Wed: ' + hrs[2][0][0] + '-' + hrs[2][0][1]
                    hours = hours + '; ' + 'Thu: ' + hrs[3][0][0] + '-' + hrs[3][0][1]
                    hours = hours + '; ' + 'Fri: ' + hrs[4][0][0] + '-' + hrs[4][0][1]
                    hours = hours + '; ' + 'Sat: ' + hrs[5][0][0] + '-' + hrs[5][0][1]
                    hours = hours + '; ' + 'Sun: ' + hrs[6][0][0] + '-' + hrs[6][0][1]
                except:
                    hours = '<MISSING>'
                hours = hours.replace(':00:00',':00').replace(':30:00',':30')
                if store not in ids:
                    ids.append(store)
                    yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        except:
            pass

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
