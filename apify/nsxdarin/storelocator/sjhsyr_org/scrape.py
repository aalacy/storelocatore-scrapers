import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

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
    locs = []
    url = 'https://sjhsyr.org/find-a-location/locations-results?LocationDescendants=true&page=1&count=100'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '{\\"Title\\":\\"' in line:
            items = line.split('{\\"Title\\":\\"')
            for item in items:
                if '"LocationNumber\\":' in item:
                    store = item.split('"LocationNumber\\":')[1].split(',')[0]
                    website = 'sjhysr.org'
                    country = 'US'
                    name = item.split('\\')[0]
                    typ = '<MISSING>'
                    try:
                        lat = item.split('"Latitude\\":\\"')[1].split('\\')[0]
                        lng = item.split('"Longitude\\":\\"')[1].split('\\')[0]
                    except:
                        lat = '<MISSING>'
                        lng = '<MISSING>'
                    loc = 'https://sjhsyr.org/' + item.split('"DirectUrl\\":\\"')[1].split('\\')[0]
                    addinfo = item.split('"LocationAddress\\":\\"')[1].split('\\')[0]
                    add = addinfo.split(',')[0].strip()
                    city = addinfo.split(',')[1].strip()
                    zc = addinfo.rsplit(' ',1)[1]
                    state = addinfo.split(',')[2].strip().rsplit(' ',1)[0]
                    phone = item.split('\\"LocationPhoneNum\\":\\"')[1].split('\\')[0]
                    hours = '<MISSING>'
                    if state == 'New':
                        state = 'New York'
                    if '5100 W' in add:
                        zc = '13088'
                    if phone == '':
                        phone = '<MISSING>'
                    if add != '':
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
