import csv
import urllib2
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
    url = 'https://www.tidedrycleaners.com/locations'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if '"title":"' in item:
                    store = item.split(',')[0]
                    website = 'tidedrycleaners.com'
                    name = item.split('"title":"')[1].split('"')[0]
                    add = item.split('"street1":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    try:
                        zc = item.split('"zip":"')[1].split('"')[0]
                    except:
                        zc = '<MISSING>'
                    country = 'US'
                    hours = item.split('"hours":"')[1].split('"')[0].replace('<br \\/>','; ')
                    try:
                        phone = item.split('"phone":"')[1].split('"')[0]
                    except:
                        phone = '<MISSING>'
                    if '"icon":"store' in item:
                        typ = 'Store'
                    else:
                        typ = ''
                    try:
                        loc = 'https://www.tidedrycleaners.com/' + item.split('"url":"')[1].split('"')[0].replace('\\','')
                    except:
                        loc = '<MISSING>'
                    if '"coordinates":[" ' in item:
                        lat = item.split('"coordinates":[" ')[1].split(',"')[1].split('"')[0]
                        lng = item.split('"coordinates":[" ')[1].split('"')[0]
                    if hours == '':
                        hours = '<MISSING>'
                    if typ == 'Store':
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
