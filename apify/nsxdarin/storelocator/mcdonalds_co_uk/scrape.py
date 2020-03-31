import csv
import urllib2
from sgrequests import SgRequests
import json
import sgzip

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'connection': 'keep-alive'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

search = sgzip.ClosestNSearch()
search.initialize(country_codes = ['gb'])

MAX_RESULTS = 25

def fetch_data():
    ids = []
    adds = []
    locations = []
    coord = search.next_coord()
    locs = []
    rad = '10'
    maxr = '25'
    while coord:
        result_coords = []
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        x, y = coord[0], coord[1]
        url = 'https://www.mcdonalds.com/googleapps/GoogleRestaurantLocAction.do?method=searchLocation&latitude=' + str(x) + '&longitude=' + str(y) + '&radius=' + rad + '&maxResults=' + maxr + '&country=gb&language=en-gb&showClosed=&hours24Text=Open%2024%20hr'
        try:
            #r = session.get(url, headers=headers, timeout=1)
            page_text = urllib2.urlopen(url).read()
            for item in json.loads(page_text)['features']:
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
                try:
                    hours = 'Mon: ' + item['properties']['restauranthours']['hoursMonday']
                    hours = hours + '; Tue: ' + item['properties']['restauranthours']['hoursTuesday']
                    hours = hours + '; Wed: ' + item['properties']['restauranthours']['hoursWednesday']
                    hours = hours + '; Thu: ' + item['properties']['restauranthours']['hoursThursday']
                    hours = hours + '; Fri: ' + item['properties']['restauranthours']['hoursFriday']
                    hours = hours + '; Sat: ' + item['properties']['restauranthours']['hoursSaturday']
                    hours = hours + '; Sun: ' + item['properties']['restauranthours']['hoursSunday']
                except:
                    hours = '<MISSING>'
                typ = 'Restaurant'
                loc = '<MISSING>'
                store = item['properties']['identifiers']['storeIdentifier'][1]['identifierValue']
                lat = item['geometry']['coordinates'][0]
                lng = item['geometry']['coordinates'][1]
                if phone == '':
                    phone = '<MISSING>'
                if city == '':
                    city = '<MISSING>'
                if store not in locs:
                    locs.append(store)
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        except:
            pass
        print("max count update")
        search.max_count_update(result_coords)
        coord = search.next_coord()


def scrape():
    data = fetch_data()
    write_output(data)

scrape()
