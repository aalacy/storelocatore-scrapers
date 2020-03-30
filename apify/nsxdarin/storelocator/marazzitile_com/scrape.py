import csv
import urllib2
from sgrequests import SgRequests
import json

session = SgRequests()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://www.marazziusa.com/where-to-buy/marazzi-showrooms'
    r = session.get(url.split(',')[0], headers=headers)
    for line in r.iter_lines():
        if '{"latitude":' in line:
            items = line.split('"auto2map":')[0].split('{"latitude":')
            for item in items:
                if ',"longitude":' in item:
                    lat = item.split(',')[0]
                    lng = item.split(',"longitude":')[1].split(',')[0]
                    surl = 'https://www.marazziusa.com/' + item.split('\\u003Ca href=\\u0022\\')[1].split('\\u0022\\u003E')[0].replace('\\/','/')
                    name = ''
                    store = ''
                    add = ''
                    city = ''
                    state = ''
                    zc = ''
                    phone = ''
                    hours = '<MISSING>'
                    country = 'US'
                    website = 'marazzitile.com'
                    r2 = session.get(surl, headers=headers)
                    print('Pulling Location %s...' % surl)
                    for line2 in r2.iter_lines():
                        if '<input type="hidden" value="' in line2:
                            store = line2.split('<input type="hidden" value="')[1].split('"')[0].strip()
                        if '<div class="showroom-title">' in line2:
                            name = line2.split('<div class="showroom-title">')[1].split('<')[0].strip()
                        if 'autocomplete="address-line1">' in line2:
                            add = line2.split('autocomplete="address-line1">')[1].split('<')[0].strip()
                            city = line2.split('autocomplete="locality">')[1].split('<')[0].strip()
                            try:
                                state = line2.split('autocomplete="region">')[1].split('<')[0].strip()
                            except:
                                state = '<MISSING>'
                            try:
                                zc = line2.split('="postal-code">')[1].split('<')[0].strip()
                            except:
                                zc = '<MISSING>'
                            try:
                                phone = line2.split('</span></div>')[1].split('<')[0].strip().replace('\t','')
                            except:
                                phone = '<MISSING>'
                    yield [website, name, add, city, state, zc, country, store, phone, "Showroom", lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
