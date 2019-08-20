import csv
import urllib2
import requests
import os
import usaddress

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "raw_address", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'http://leiszler.com/locations.aspx'
    r = session.get(url, headers=headers)
    lines = r.iter_lines()
    for line in lines:
        if 'var myLatlng' in line:
            lat = line.split('(')[1].split(',')[0]
            lng = line.split(',')[1].split(')')[0]
            website = 'leiszler.com'
            typ = 'Store'
            hours = '<MISSING>'
            g = next(lines)
            address = ''
            city = ''
            state = ''
            zc = ''
            rawadd = g.split('input name="daddr" value="')[1].split('"')[0]
            try:
                add = usaddress.tag(rawadd)
                baseadd = add[0]
                if 'AddressNumber' not in baseadd:
                    baseadd['AddressNumber'] = ''
                if 'StreetName' not in baseadd:
                    baseadd['StreetName'] = ''
                if 'StreetNamePostType' not in baseadd:
                    baseadd['StreetNamePostType'] = ''
                if 'PlaceName' not in baseadd:
                    baseadd['PlaceName'] = '<INACCESSIBLE>'
                if 'StateName' not in baseadd:
                    baseadd['StateName'] = '<INACCESSIBLE>'
                if 'ZipCode' not in baseadd:
                    baseadd['ZipCode'] = '<INACCESSIBLE>'
                address = add[0]['AddressNumber'] + ' ' + add[0]['StreetName'] + ' ' + add[0]['StreetNamePostType']
                address = address.encode('utf-8')
                if address == '':
                    address = '<INACCESSIBLE>'
                city = add[0]['PlaceName'].encode('utf-8')
                state = add[0]['StateName'].encode('utf-8')
                zc = add[0]['ZipCode'].encode('utf-8')
            except:
                rawadd = rawadd.strip()
            name = g.split("content: '")[1].split('<')[0]
            country = 'US'
            store = g.split('Short Stop #')[1].split('<')[0]
            phone = g.split('<br />')[2].split('<')[0]
            yield [website, name, rawadd, address, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
