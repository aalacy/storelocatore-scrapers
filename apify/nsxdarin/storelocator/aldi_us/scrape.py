import csv
import urllib2
from sgrequests import SgRequests
import sgzip

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

MAX_RESULTS = 20
MAX_DISTANCE = 5.0

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    ids = set()
    locations = []
    coord = search.next_zip()
    while coord:
        print("remaining zipcodes: " + str(len(search.zipcodes)))
        website = 'aldi.us'
        print('%s...' % coord)
        url = 'https://www.aldi.us/stores/en-us/Search?SingleSlotGeo=' + coord + '&Mode=None'
        r = session.get(url, headers=headers)
        result_coords = []
        purl = '<MISSING>'
        typ = 'Store'
        array = []
        for line in r.iter_lines():
            if '<li tabindex="' in line:
                try:
                    lng = line.split('locX&quot;:&quot;')[1].split('&')[0]
                    lat = line.split('locY&quot;:&quot;')[1].split('&')[0]
                except:
                    lat = '<MISSING>'
                    lng = '<MISSING>'
            if 'itemprop="name">' in line:
                hours = ''
                name = line.split('itemprop="name">')[1].split('<')[0]
            if '"streetAddress" class="resultItem-Street">' in line:
                add = line.split('"streetAddress" class="resultItem-Street">')[1].split('<')[0]
            if 'class="resultItem-City" data-city="' in line:
                try:
                    city = line.split('class="resultItem-City" data-city="')[1].split(',')[0]
                    state = line.split('class="resultItem-City" data-city="')[1].split(',')[1].split('"')[0].strip()
                    zc = line.split('">')[1].split('<')[0].strip().rsplit(' ',1)[1]
                    country = 'US'
                    store = '<MISSING>'
                    phone = '<MISSING>'
                except:
                    state = '<MISSING>'
            if '<td class="open">' in line:
                if hours == '':
                    hours = line.split('<td class="open">')[1].split('<')[0] + ': '
                else:
                    hours = hours + '; ' + line.split('<td class="open">')[1].split('<')[0] + ': '
            if '<td class="open openingTime">' in line:
                hours = hours + line.split('<td class="open openingTime">')[1].split('<')[0]
            if '<div class="onlyMobile resultItem-Arrow">' in line:
                info = add + ';' + city + ';' + state
                ids.add(info)
                array.append(info)
                if info not in locations:
                    locations.append(info)
                    if hours == '':
                        hours = '<MISSING>'
                    if state != '<MISSING>':
                        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
        if len(array) <= MAX_RESULTS:
            print("max distance update")
            search.max_distance_update(MAX_DISTANCE)
        else:
            raise Exception("expected at most " + str(MAX_RESULTS) + " results")
        coord = search.next_zip()

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
