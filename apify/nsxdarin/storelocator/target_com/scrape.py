import csv
from sgrequests import SgRequests
import sgzip

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
    ids = []
    r = session.get('https://www.target.com/store-locator/find-stores/', headers=headers)
    key = ''
    for line in r.iter_lines():
        line = str(line.decode('utf-8'))
        if '"apiKey\\":\\"' in line:
            key = line.split('"apiKey\\":\\"')[1].split('\\')[0]
    print(key)
    for code in sgzip.for_radius(100):
        print('Pulling Zip Code %s...' % code)
        url = 'https://redsky.target.com/v3/stores/nearby/' + code + '?key=' + key + '&limit=500&within=100&unit=mile'
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            line = str(line.decode('utf-8')).replace('"drive_up":{"location_id":"','')
            if '"location_id":' in line:
                items = line.split('"location_id":')
                for item in items:
                    if 'type_code' in item:
                        store = item.split(',')[0]
                        website = 'target.com'
                        typ = item.split('"sub_type_code":"')[1].split('"')[0]
                        add = item.split('"address_line1":"')[1].split('"')[0]
                        if 'address_line2' in item:
                            add = add + ' ' + item.split('"address_line2":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"region":"')[1].split('"')[0]
                        zc = item.split('"postal_code":"')[1].split('"')[0]
                        lat = item.split(',"geographic_specifications":{"latitude":')[1].split(',')[0]
                        lng = item.split(',"geographic_specifications":{"latitude":')[1].split('"longitude":')[1].split(',')[0]
                        name = item.split('"name":"')[1].split('"')[0]
                        loc = 'https://www.target.com/sl/' + name.lower().replace(' ','-') + '/' + store
                        country = 'US'
                        phone = item.split('"telephone_number":"')[1].split('"')[0]
                        r2 = session.get(loc, headers=headers)
                        hours = ''
                        if store not in ids:
                            print(loc)
                            ids.append(store)
                            for line2 in r2.iter_lines():
                                line2 = str(line2.decode('utf-8'))
                                if ',"openingHoursSpecification":[' in line2 and hours == '':
                                    days = line2.split(',"openingHoursSpecification":[')[1].split(']')[0].split('"dayOfWeek":"')
                                    for day in days:
                                        if '"opens":"' in day:
                                            hrs = day.split('"')[0] + ': ' + day.split('"opens":"')[1].split('"')[0].rsplit(':',1)[0] + '-' + day.split('"closes":"')[1].split('"')[0].rsplit(':',1)[0]
                                            if hours == '':
                                                hours = hrs
                                            else:
                                                hours = hours + '; ' + hrs
                            yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
