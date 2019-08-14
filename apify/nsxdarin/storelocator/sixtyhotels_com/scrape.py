import csv
import urllib2
import requests

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
    url = 'https://www.sixtyhotels.com/'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<li id="menu-item-' in line and 'Explore More</span><span>' in line:
            hotel = line.split('href="')[1].split('"')[0]
            r2 = session.get(hotel, headers=headers)
            website = 'sixtyhotels.com'
            hours = '<MISSING>'
            store = '<MISSING>'
            country = 'US'
            typ = 'Hotel'
            name = ''
            add = ''
            city = '<MISSING>'
            state = ''
            zc = '<MISSING>'
            phone = ''
            for line2 in r2.iter_lines():
                if '<a class="hotelinfo-phone" href="tel:+' in line2:
                    phone = line2.split('<a class="hotelinfo-phone" href="tel:+')[1].split('"')[0].replace('.','-')
                if '<title>' in line2 and '</title>' in line2:
                    name = line2.split('<title>')[1].split(' |')[0]
                if '<a class="hotelinfo-address"' in line2:
                    add = line2.split('<a class="hotelinfo-address"')[1].split('">')[1].split(',')[0]
                    state = line2.split('<a class="hotelinfo-address"')[1].split('">')[1].split(',')[1].split('<')[0]
                if 'jmappingAPI_map.setCenter({ lat: ' in line2:
                    lat = line2.split('jmappingAPI_map.setCenter({ lat: ')[1].split(',')[0]
                    lng = line2.split('lng: ')[1].split('}')[0].strip()
            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
