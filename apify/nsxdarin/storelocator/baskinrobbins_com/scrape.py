import csv
import urllib.request, urllib.error, urllib.parse
import json
from sgrequests import SgRequests
from sglogging import SgLogSetup

logger = SgLogSetup().get_logger('baskinrobbins_com')



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
    locs = []
    urls = ['https://order.baskinrobbins.com/mobilem8-web-service/rest/storeinfo/distance?attributes=&radius=1500&disposition=DELIVERY&latitude=34.0661071&longitude=-110.38417770000001&maxResults=1000&tenant=br-us',
            'https://order.baskinrobbins.com/mobilem8-web-service/rest/storeinfo/distance?attributes=&radius=1500&disposition=DELIVERY&latitude=44.0661071&longitude=-95.38417770000001&maxResults=1000&tenant=br-us',
            'https://order.baskinrobbins.com/mobilem8-web-service/rest/storeinfo/distance?attributes=&radius=1500&disposition=DELIVERY&latitude=34.0661071&longitude=-85.38417770000001&maxResults=1000&tenant=br-us',
            'https://order.baskinrobbins.com/mobilem8-web-service/rest/storeinfo/distance?attributes=&radius=1500&disposition=DELIVERY&latitude=44.0661071&longitude=-75.38417770000001&maxResults=1000&tenant=br-us',
            'https://order.baskinrobbins.com/mobilem8-web-service/rest/storeinfo/distance?attributes=&radius=1500&disposition=DELIVERY&latitude=21.0661071&longitude=-155.38417770000001&maxResults=1000&tenant=br-us',
            'https://order.baskinrobbins.com/mobilem8-web-service/rest/storeinfo/distance?attributes=&radius=1500&disposition=DELIVERY&latitude=60.0661071&longitude=-150.38417770000001&maxResults=1000&tenant=br-us'
            ]
    for url in urls:
        logger.info(url)
        r = session.get(url, headers=headers)
        array = json.loads(r.content)
        items = array['getStoresResult']['stores']
        for item in items:
            name = 'Baskin Robbins'
            typ = 'Store'
            store = item['storeName']
            status = item['status']
            city = item['city']
            add = item['street']
            state = item['state']
            country = 'US'
            zc = item['zipCode']
            lat = item['latitude']
            lng = item['longitude']
            website = 'baskinrobbins.com'
            try:
                phone = item['phoneNumber']
            except:
                phone = '<MISSING>'
            try:
                hours = 'Mon: ' + item['storeHours'][0]['monday']['openTime']['timeString'].split(',')[0] + '-' + item['storeHours'][0]['monday']['closeTime']['timeString'].split(',')[0]
                hours = hours + '; Tue: ' + item['storeHours'][0]['tuesday']['openTime']['timeString'].split(',')[0] + '-' + item['storeHours'][0]['tuesday']['closeTime']['timeString'].split(',')[0]
                hours = hours + '; Wed: ' + item['storeHours'][0]['wednesday']['openTime']['timeString'].split(',')[0] + '-' + item['storeHours'][0]['wednesday']['closeTime']['timeString'].split(',')[0]
                hours = hours + '; Thu: ' + item['storeHours'][0]['thursday']['openTime']['timeString'].split(',')[0] + '-' + item['storeHours'][0]['thursday']['closeTime']['timeString'].split(',')[0]
                hours = hours + '; Fri: ' + item['storeHours'][0]['friday']['openTime']['timeString'].split(',')[0] + '-' + item['storeHours'][0]['friday']['closeTime']['timeString'].split(',')[0]
                hours = hours + '; Sat: ' + item['storeHours'][0]['saturday']['openTime']['timeString'].split(',')[0] + '-' + item['storeHours'][0]['saturday']['closeTime']['timeString'].split(',')[0]
                hours = hours + '; Sun: ' + item['storeHours'][0]['sunday']['openTime']['timeString'].split(',')[0] + '-' + item['storeHours'][0]['sunday']['closeTime']['timeString'].split(',')[0]
            except:
                hours = '<MISSING>'
            if add != '':
                if store not in locs:
                    locs.append(store)
                    yield [website, name, add, city, state, zc, country, store, phone, typ, lat, lng, hours]

def scrape():
    data = fetch_data()
    write_output(data)

scrape()
