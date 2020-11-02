import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

requests.packages.urllib3.disable_warnings()

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
    url = 'https://justsalad.com/assets/geo/js.geojson?v=1558558583021'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if '"locationID": "' in line:
            store = line.split('"locationID": "')[1].split('"')[0]
            hours = ''
            state = '<MISSING>'
            website = 'justsalad.com'
            country = 'US'
            city = '<MISSING>'
            zc = '<MISSING>'
            typ = 'Restaurant'
        if '"state":"' in line:
            state = line.split('"state":"')[1].split('"')[0]
        if '"locationName": "' in line:
            name = line.split('"locationName": "')[1].split('"')[0]
        if '"locationAddress": "' in line:
            add = line.split('"locationAddress": "')[1].split('"')[0]
        if '"locationPhone": "' in line:
            phone = line.split('"locationPhone": "')[1].split('"')[0]
        if '"hours' in line and '""' not in line:
            hrs = line.split('": "')[1].split('"')[0]
            if hours == '':
                hours = hrs
            else:
                hours = hours + '; ' + hrs
        if '"coordinates":' in line:
            g = next(lines)
            h = next(lines)
            lng = g.split(',')[0].strip().replace('\t','')
            lat = h.strip().replace('\t','').replace('\r','').replace('\n','')
            loc = '<MISSING>'
            if '-' in lng:
                if state == '<MISSING>':
                    if '40.6' in lat or '40.7' in lat:
                        state = 'NY'
                        city = 'New York'
                    if 'Newport' in name:
                        state = 'NJ'
                        city = 'Jersey City'
                    if state == '<MISSING>':
                        state = 'PA'
                        city = 'Philadelphia'
                if hours == '':
                    hours = '<MISSING>'
                if '-8' in lng:
                    state = 'IL'
                    city = 'Chicago'
                if 'Woodbury Common' in name:
                    state = 'NY'
                    city = 'Central Valley'
                yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
