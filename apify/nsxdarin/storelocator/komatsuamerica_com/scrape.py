import csv
import urllib.request, urllib.error, urllib.parse
from sgrequests import SgRequests

session = SgRequests()
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "page_url", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    locs = []
    url = 'https://www.komatsuamerica.com/apimaps/getdistributors'
    payload = {'lat': 30,
               'lng': -95,
               'radius': 10000
               }
    r = session.post(url, headers=headers, data=payload)
    if r.encoding is None: r.encoding = 'utf-8'
    website = 'komatsuamerica.com'
    for line in r.iter_lines(decode_unicode=True):
        if '"CompanyName":"' in line:
            items = line.split('"CompanyName":"')
            for item in items:
                if '"PhoneNumber":"' in item:
                    name = item.split('"')[0]
                    phone = item.split('"PhoneNumber":"')[1].split('"')[0]
                    try:
                        loc = item.split('"Website":"')[1].split('"')[0]
                    except:
                        loc = '<MISSING>'
                    if loc == '':
                        loc = '<MISSING>'
                    lng = item.split('"Longitude":')[1].split(',')[0]
                    lat = item.split('"Latitude":')[1].split(',')[0]
                    add = item.split('"Address":"')[1].split('"')[0]
                    try:
                        typ = item.split('"EquipmentTypes":[')[1].split(']')[0].replace('"','')
                    except:
                        typ = '<MISSING>'
                    state = item.split('"State":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    zc = item.split('"Zip":"')[1].split('"')[0]
                    store = '<MISSING>'
                    country = 'US'
                    hours = '<MISSING>'
                    if ' ' in zc:
                        country = 'CA'
                    if state == '' or city == '' or state == 'XX':
                        pass
                    else:
                        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
