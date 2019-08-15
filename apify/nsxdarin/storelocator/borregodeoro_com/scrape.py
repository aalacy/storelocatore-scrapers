import csv
import urllib2
import requests
import json

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36',
           'content-type': 'application/json',
           'X-Requested-With': 'XMLHttpRequest'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'http://borregodeoro.com/contact.html'
    r = session.get(url, headers=headers)
    typ = 'Restaurant'
    website = 'borregodeoro.com'
    country = 'US'
    lat = '<MISSING>'
    lng = '<MISSING>'
    Found = True
    num = 0
    lines = r.iter_lines()
    for line in lines:
        if 'Contact</p></div></a>' in line:
            Found = True
        if Found and '<div class="colelem"' in line:
            Found = False
        if Found and 'div class="clearfix grpelem"' in line:
            num = num + 1
            name = 'Borrego ' + str(num)
            store = str(num)
            add = next(lines).split('>')[1].split('<')[0]
            g = next(lines)
            city = g.split('>')[1].split(',')[0]
            state = g.split('>')[1].split(',')[1].strip().split(' ')[0]
            zc = g.split(',')[1].split('<')[0].rsplit(' ',1)[1]
            next(lines)
            phone = next(lines).split('>')[1].split('<')[0].replace('&#45;','-')
            hours = '<MISSING>'
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
