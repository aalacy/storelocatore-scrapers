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
    url = 'https://www.hyundaiusa.com/var/hyundai/services/dealer/dealersByZip.json?brand=hyundai&model=all&lang=en_US&zip=51448&maxdealers=1000'
    r = session.get(url, headers=headers)
    if r.encoding is None: r.encoding = 'utf-8'
    for line in r.iter_lines(decode_unicode=True):
        if '{"cobaltDealerURL":"' in line:
            items = line.split('{"cobaltDealerURL":"')
            for item in items:
                if '"redCapUrl":' in item:
                    website = 'hyundaiusa.com'
                    typ = '<MISSING>'
                    loc = '<MISSING>'
                    store = item.split('"dealerCd":"')[1].split('"')[0]
                    name = item.split('"dealerNm":"')[1].split('"')[0]
                    add = item.split('"address1":"')[1].split('"')[0] + ' ' + item.split('"address2":"')[1].split('"')[0]
                    add = add.strip()
                    country = 'US'
                    city = item.split('"city":"')[1].split('"')[0]
                    zc = item.split(',"zipCd":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split('e')[0]
                    lng = item.split('"longitude":')[1].split('e')[0]
                    lat = float(lat) * 10
                    lng = float(lng) * 10
                    lat = str(lat)
                    lng = str(lng)
                    hours = ''
                    if '"operations":[]' in item:
                        hours = '<MISSING>'
                    else:
                        days = item.split('"operations":[')[1].split(']')[0].split('"name":"')
                        for day in days:
                            if '"hour":"' in day:
                                hrs = day.split('"day":"')[1].split('"')[0] + ': ' + day.split('"hour":"')[1].split('"')[0]
                                if hours == '':
                                    hours = hrs
                                else:
                                    hours = hours + '; ' + hrs
                    yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
