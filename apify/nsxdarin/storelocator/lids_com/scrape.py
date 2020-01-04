import csv
import urllib2
import requests

session = requests.Session()
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
    url = 'https://www.lids.com/sitemaplidsstorelocations.xml'
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<url><loc>https://www.lids.com/store/' in line:
            locs.append(line.split('<loc>')[1].split('<')[0])
    for loc in locs:
        website = 'lids.com'
        typ = '<MISSING>'
        hours = ''
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '"storeId":"' in line2:
                store = line2.split('"storeId":"')[1].split('"')[0]
                name = line2.split('"storeId":"')[1].split('"name":"')[1].split('"')[0]
                add = line2.split('"storeId":"')[1].split('"address1":"')[1].split('"')[0]
                try:
                    add = add + ' ' + line2.split('"storeId":"')[1].split('"address2":"')[1].split('"')[0]
                    add = add.strip()
                except:
                    pass
                city = line2.split('"storeId":"')[1].split('"city":"')[1].split('"')[0]
                phone = line2.split('"storeId":"')[1].split('"phone":"')[1].split('"')[0]
                state = line2.split('"storeId":"')[1].split('"state":"')[1].split('"')[0]
                zc = line2.split('"storeId":"')[1].split('"zip":"')[1].split('"')[0]
                lat = line2.split('"storeId":"')[1].split('"latitude":"')[1].split('"')[0]
                lng = line2.split('"storeId":"')[1].split('"longitude":"')[1].split('"')[0]
                country = 'US'
            if '<td class="day">' in line2:
                days = line2.split('<td class="day">')
                for day in days:
                    if 'columns store-hours">' not in day:
                        hrs = day.split('<')[0] + ': ' + day.split('</td><td>')[1] + '-' + day.split('</td><td>')[3].split('<')[0]
                        if hours == '':
                            hours = hrs
                        else:
                            hours = hours + '; ' + hrs
        if hours == '':
            hours = '<MISSING>'
        if phone == '':
            phone = '<MISSING>'
        yield [website, loc, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
