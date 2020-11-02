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
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://sunriseconveniencestores.com'
    locs = []
    cities = []
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    lines = r.iter_lines(decode_unicode=True)
    for line in lines:
        if '"title":"' in line:
            items = line.split('"title":"')
            for item in items:
                if '"address":"' in item:
                    add = item.split('"address":"')[1].split(',')[0]
                    name = item.split('">')[1].split('<')[0]
                    website = 'sunriseconveniencestores.com'
                    if 'BP' in name:
                        typ = 'BP'
                    else:
                        typ = 'Marathon'
                    store = '<MISSING>'
                    zc = '<MISSING>'
                    if '&output=classic' in item:
                        zc = item.split('&output=classic')[0].rsplit('+',1)[1]
                    city = item.split('"address":"')[1].split('","desc')[0].split(',')[1].strip()
                    try:
                        state = item.split('"address":"')[1].split('","desc')[0].split(',')[2].split('"')[0].strip()
                    except:
                        city = item.split('"address":"')[1].split('","desc')[0].split(',')[1].rsplit(' ',1)[0].strip()
                        state = item.split('"address":"')[1].split('","desc')[0].split(',')[1].rsplit(' ',1)[1].strip()
                    country = 'US'
                    phone = item.split('"tel:+')[1].split('\\')[0]
                    hours = item.split('"desc":"')[1].split('<\\/a>\\n<p>')[1].split('<')[0]
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    if '-' in name:
                        name = city + ' Marathon'
                    if '\\' in hours:
                        hours = hours.split('\\')[0]
                    if zc == '':
                        zc = '<MISSING>'
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
