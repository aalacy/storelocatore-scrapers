import csv
import urllib2
from sgrequests import SgRequests
import sgzip
import json

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
    ids = []
    for code in sgzip.for_radius(100):
        print('Pulling Zip Code %s...' % code)
        url = 'https://www.ford.com/services/dealer/Dealers.json?make=Ford&radius=500&filter=&minDealers=1&maxDealers=100&postalCode=' + code
        LFound = True
        while LFound:
            try:
                LFound = False
                r = session.get(url, headers=headers, timeout=10)
                if '"Dealer":[{' in r.content:
                    for item in json.loads(r.content)['Response']['Dealer']:
                        lng = item['Longitude']
                        lat = item['Latitude']
                        name = item['Name']
                        typ = item['dealerType']
                        website = 'ford.com'
                        purl = item['URL']
                        hours = ''
                        add = item['Address']['Street1'] + ' ' + item['Address']['Street2'] + ' ' + item['Address']['Street3']
                        add = add.strip()
                        city = item['Address']['City']
                        state = item['Address']['State']
                        country = item['Address']['Country'][:2]
                        zc = item['Address']['PostalCode']
                        store = item['SalesCode']
                        phone = item['Phone']
                        daytext = str(item['SalesHours'])
                        daytext = daytext.replace("'",'"')
                        daytext = daytext.replace('u"','"').replace(' {','{')
                        days = daytext.split(',{')
                        for day in days:
                            if '"name": "' in day:
                                dname = day.split('"name": "')[1].split('"')[0]
                                if '"closed": "true"' in day:
                                    hrs = 'Closed'
                                else:
                                    hrs = day.split('"open": "')[1].split('"')[0] + '-' + day.split('"close": "')[1].split('"')[0]
                                if hours == '':
                                    hours = dname + ': ' + hrs
                                else:
                                    hours = hours + '; ' + dname + ': ' + hrs
                        if store not in ids:
                            ids.append(store)
                            if hours == '':
                                hours = '<MISSING>'
                            if purl == '':
                                purl = '<MISSING>'
                            if phone == '':
                                phone = '<MISSING>'
                            yield [website, purl, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]
            except:
                LFound = True

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
