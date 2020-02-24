import csv
import urllib2
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
    url = 'https://swgaoil.com/wp-content/themes/southwestgaoil/get-locations.php?origAddress='
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '"id":' in line:
            items = line.split('"id":')
            for item in items:
                if '"name":"' in item:
                    name = item.split('"name":"')[1].split('"')[0]
                    lurl = item.split('"web":"')[1].split('"')[0].replace('\\','')
                    add = item.split('"address":"')[1].split('"')[0] + ' ' + item.split('"address2":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"postal":"')[1].split('"')[0]
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    linfo = lurl + '|' + name + '|' + add + '|' + city + '|' + state + '|' + zc + '|' + lat + '|' + lng
                    locs.append(linfo)
    for loc in locs:
        Found = False
        print('Pulling Location %s...' % loc.split('|')[0])
        llink = loc.split('|')[0]
        website = 'swgaoil.com/ss-food-stores'
        name = loc.split('|')[1]
        add = loc.split('|')[2]
        city = loc.split('|')[3]
        state = loc.split('|')[4]
        zc = loc.split('|')[5]
        lat = loc.split('|')[6]
        lng = loc.split('|')[7]
        store = '<MISSING>'
        country = 'US'
        typ = '<MISSING>'
        hours = '<MISSING>'
        phone = '<MISSING>'
        if '#' in name:
            store = name.rsplit('#',1)[1]
        yield [website, llink, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
