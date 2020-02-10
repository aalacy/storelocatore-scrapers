import csv
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
    states = []
    url = 'https://www.verizonwireless.com/stores'
    r = session.get(url, headers=headers)
    SFound = False
    for line in r.iter_lines():
        if '{"states":[{"' in line and SFound is False:
            SFound = True
            items = line.split('{"name":"')
            for item in items:
                if '"url":"/stores/' in item:
                    states.append('https://www.verizonwireless.com' + item.split('"url":"')[1].split('"')[0])
    for state in states:
        #print('Pulling State %s...' % state)
        locs = []
        cities = []
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if '"cities":' in line2:
                items = line2.split('{"name":"')
                for item in items:
                    if '","url":"' in item and 'var stateJSON' not in item:
                        cities.append('https://www.verizonwireless.com' + item.split('"url":"')[1].split('"')[0])
        for city in cities:
            #print('Pulling City %s...' % city)
            r3 = session.get(city, headers=headers)
            for line3 in r3.iter_lines():
                if '"stores":' in line3:
                    items = line3.split('{"storeName":"')
                    for item in items:
                        if 'var cityJSON' not in item:
                            website = 'verizonwireless.com'
                            name = item.split('"')[0]
                            add = item.split('"address":"')[1].split('"')[0]
                            city = item.split(',"city":"')[1].split('"')[0]
                            loc = 'https://www.verizonwireless.com' + item.split('"storeUrl":"')[1].split('"')[0]
                            lat = item.split('"lat":"')[1].split('"')[0]
                            lng = item.split('"lng":"')[1].split('"')[0]
                            try:
                                phone = item.split('"phone":"')[1].split('"')[0]
                            except:
                                phone = '<MISSING>'
                            state = item.split('"stateAbbr":"')[1].split('"')[0]
                            country = 'US'
                            typ = item.split('"typeOfStore":["')[1].split(']')[0].replace('"','')
                            hours = item.split('"openingHours":{')[1].split('}')[0].replace('":"',': ').replace('","','; ').replace('"','')
                            zc = item.split(',"zip":')[1].split(',')[0]
                            store = item.split('"netaceLocationCode":"')[1].split('"')[0]
                            if hours == '':
                                hours = '<MISSING>'
                            yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
