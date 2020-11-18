import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import sgzip

from sglogging import SgLogSetup
logger = SgLogSetup().get_logger('aldi_us')

search = sgzip.ClosestNSearch()
search.initialize()

session = SgRequests()
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',',
                            quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip",
                         "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)



def fetch_data():

    locations_all = []
    coord = search.next_zip()
    while coord:
        website = 'aldi.us'
        logger.info(coord)
        url = 'https://www.aldi.us/stores/en-us/Search?SingleSlotGeo=' + coord + '&Mode=None'
        r = session.get(url, headers=headers)
        if r.encoding is None: r.encoding = 'utf-8'
        locations_this_url = []
        purl = '<MISSING>'
        typ = 'Store'
        phone = '<MISSING>'
        for line in r.iter_lines(decode_unicode=True):
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
                add = line.split(
                    '"streetAddress" class="resultItem-Street">')[1].split('<')[0]
            if 'itemprop="telephone" href="tel:' in line:
                phone = line.split('itemprop="telephone" href="tel:')[1].split('"')[0]
            if 'class="resultItem-City" data-city="' in line:
                try:
                    city = line.split(
                        'class="resultItem-City" data-city="')[1].split(',')[0]
                    state = line.split(
                        'class="resultItem-City" data-city="')[1].split(',')[1].split('"')[0].strip()
                    zc = line.split('">')[1].split(
                        '<')[0].strip().rsplit(' ', 1)[1]
                    country = 'US'
                    store = '<MISSING>'
                except:
                    state = '<MISSING>'
            if '<td class="open">' in line:
                if hours == '':
                    hours = line.split('<td class="open">')[1].split('<')[0] + ': '
                else:
                    hours = hours + '; ' + \
                        line.split('<td class="open">')[1].split('<')[0] + ': '
            if '<td class="open openingTime">' in line:
                hours = hours + \
                    line.split('<td class="open openingTime">')[1].split('<')[0]
            if '<div class="onlyMobile resultItem-Arrow">' in line:

                location_info = {'address': add, 'city': city, 'state': state, 'lat': lat, 'lng': lng}
                locations_this_url.append(location_info)

                if location_info not in locations_all:
                    locations_all.append(location_info)
                    if hours == '':
                        hours = '<MISSING>'
                    if state != '<MISSING>':
                        yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]


        result_coords = []
        for loc in locations_this_url:
            result_coords.append((loc['lat'], loc['lng']))
        search.max_count_update(result_coords)

        coord = search.next_zip()



def scrape():
    data = fetch_data()
    write_output(data)


scrape()
