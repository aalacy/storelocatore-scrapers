import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation", "page_url"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://public.websteronline.com/location'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if 'script type="application/json"' in line:
            raw_json = '{' + line.rsplit('}', 1)[0].split('{', 1)[1] + '}'
            locations = json.loads(raw_json)['wbLocationFinder']['locations']
            website = 'public.websteronline.com'
            for location in locations:
                attrs = location['attributes']
                typ = 'branch' if attrs['branch'] else 'atm'
                store = location['id']
                address = attrs['address']
                add = address['street_1']
                zc = address['zip']
                state = address['state']
                city = address['city']
                country = address['country']
                name = attrs['title'] 
                phone = attrs['phone']
                days = attrs['open_hours']
                hours = '<MISSING>'
                if days:
                    hours_list = []
                    for day in days.keys():
                        if not days[day]:
                            hours_list.append('{}: closed'.format(day))
                        else:
                            hours_list.append('{}: {}-{}'.format(day, days[day][0]['start']['formatted'], days[day][0]['end']['formatted']))
                    hours = ', '.join(hours_list)
                lat = attrs['geolocation']['lat']
                lng = attrs['geolocation']['lng']
                page_url = location['url']
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours, page_url]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
