import csv
import urllib2
import requests

requests.packages.urllib3.disable_warnings()

session = requests.Session()
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
           }

def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code", "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation"])
        for row in data:
            writer.writerow(row)

def fetch_data():
    url = 'https://info.lululemon.com/stores?mnid=ftr;en-US;store-locator'
    locs = []
    r = session.get(url, headers=headers, verify=False)
    for line in r.iter_lines():
        if "type: '" in line:
            stype = line.split("type: '")[1].split("'")[0]
        if '<h1><a href="https://shop.lululemon.com/stores/ca/' in line or '<h1><a href="https://shop.lululemon.com/stores/us/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            locs.append(lurl + '|' + stype)
    print('Found %s Locations.' % str(len(locs)))
    for loc in locs:
        print('Pulling Location %s...' % loc.split('|')[0])
        website = 'lululemon.com'
        typ = loc.split('|')[1]
        hours = ''
        store = '<MISSING>'
        locurl = loc.split('|')[0]
        r2 = session.get(locurl, headers=headers, verify=False)
        for line2 in r2.iter_lines():
            if ',"streetAddress":"' in line2:
                add = line2.split(',"streetAddress":"')[1].split('"')[0]
                phone = line2.split('"telephone":"')[1].split('"')[0]
                city = line2.split(',"addressLocality":"')[1].split('"')[0]
                state = line2.split('"addressRegion":"')[1].split('"')[0]
                country = line2.split('"addressCountry":"')[1].split('"')[0]
                lat = line2.split(',"latitude":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                lng = line2.split(',"longitude":"')[1].split('"')[0]
                name = line2.split('"photo":{')[1].split('"name":"')[1].split('"')[0]
                hours = line2.split('"openingHours":[')[1].split(']')[0].replace('","','; ').replace('"','')
                if hours == '':
                    hours = '<MISSING>'
                if 'null' in hours:
                    hours = '<MISSING>'
                if phone == '':
                    phone = '<MISSING>'
                if hours == '':
                    hours = '<MISSING>'
                yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
